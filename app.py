import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Конфигурация страницы
st.set_page_config(page_title="Energy OS | Partner Panel", page_icon="⚡", layout="wide")

# Убираем "белую хуйню" и фиксируем видимость текста
st.markdown("""
    <style>
    /* Главный фон и шрифт */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Стилизация верхних карточек (Metrics) */
    [data-testid="stMetric"] {
        background-color: #1A1C24 !important;
        border: 1px solid #262730 !important;
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }
    
    /* Цвет цифр в метриках */
    [data-testid="stMetricValue"] {
        color: #00FFC2 !important; /* Неоновый зеленый */
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem !important;
    }
    
    /* Цвет подписей в метриках */
    [data-testid="stMetricLabel"] {
        color: #808495 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.8rem !important;
    }

    /* Стилизация таблицы (Dataframe) */
    .stDataFrame {
        border: 1px solid #262730 !important;
        border-radius: 10px !important;
    }

    /* Стилизация заголовков */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Плашка Info/Success */
    .stAlert {
        background-color: #1A1C24 !important;
        border: 1px solid #00FFC2 !important;
        color: #FFFFFF !important;
    }

    /* Убираем стандартный хедер Streamlit для чистоты */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Настройка разделителя */
    hr {
        border-top: 1px solid #262730 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Хедер с бизнес-оффером
st.title("⚡️ Energy OS: System Zarządzania Autokonsumpcją")
st.info("💡 **Status B2B:** System gotowy do wdrożenia pod Twoją marką (White-Label).")

col_text, col_badge = st.columns([3, 1])
with col_text:
    st.markdown("""
    ### Rozwiązanie problemów sieciowych 253V + Optymalizacja RCE
    Nasza technologia pozwala Twoim klientom uniknąć wyłączeń falownika i maksymalnie wykorzystać darmową energię. 
    **Zgodność z dotacjami Mój Prąd (Systemy EMS/HEMS).**
    """)
with col_badge:
    st.success("Certyfikacja RCE 2026")

# Подключение к базе (только чтение)
def load_data():
    try:
        conn = sqlite3.connect("triggers.db")
        df_logs = pd.read_sql_query("SELECT timestamp, user_label, reason, price_pln_mwh FROM execution_logs", conn)
        df_users = pd.read_sql_query("SELECT user_label, threshold_pln_mwh FROM user_triggers WHERE is_active=1", conn)
        conn.close()
        return df_logs, df_users
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

df_logs, df_users = load_data()

if not df_users.empty or not df_logs.empty:
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("Monitorowane Obiekty", len(df_users))
    with m2:
        today = datetime.now().strftime('%Y-%m-%d')
        today_triggers = len(df_logs[df_logs['timestamp'].str.startswith(today)]) if not df_logs.empty else 0
        st.metric("Interwencje (Dziś)", today_triggers)
    with m3:
        overvoltage_count = len(df_logs[df_logs['reason'].str.contains("253V")])
        st.metric("Uratowane Cykle 253V", overvoltage_count)
    with m4:
        min_price = df_logs['price_pln_mwh'].min() if not df_logs.empty else 0
        st.metric("Najniższa Cena RCE", f"{min_price:.2f} PLN")

    st.divider()

    col_table, col_info = st.columns([2, 1])

    with col_table:
        st.subheader("📋 Ostatnie operacje systemowe")
        if not df_logs.empty:
            df_display = df_logs.sort_values(by="timestamp", ascending=False).head(15)
            df_display.columns = ['Data/Godzina', 'ID Klienta', 'Typ Akcji', 'Cena (PLN/MWh)']
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("Oczekiwanie na pierwsze zdarzenia rynkowe...")

    with col_info:
        st.subheader("🛠 Narzędzia Partnera")
        with st.expander("🛡 Ochrona Napięciowa 253V"):
            st.write("Algorytm aktywuje zrzut energii na grzałki przy 252.5V.")
            st.progress(0.95, text="Skuteczność: 95%")
        
        with st.expander("📈 Optymalizacja Taryf RCE"):
            st.write("Automatyczny start pomp ciepła и ловарок EV.")
            st.button("Pobierz raport oszczędności (PDF)", use_container_width=True)
        
        st.warning("📅 **Next update:** Integracja z magazynami energii (BESS) - Q3 2026")

else:
    st.error("⚠️ Brak połąчения z bazą данных.")

st.markdown("---")
col_bot_l, col_bot_r = st.columns(2)
with col_bot_l:
    st.caption("© 2026 Energy OS System | Powered by ENTSO-E & Shelly Cloud API")
with col_bot_r:
    st.markdown("<p style='text-align:right; color:gray;'>Wsparcie techniczne: 24/7</p>", unsafe_allow_html=True)
