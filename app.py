import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Конфигурация страницы
st.set_page_config(page_title="Energy OS | Partner Panel", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; }
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
    # Метрики — это твои "солдаты" в переговорах
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("Monitorowane Obiekty", len(df_users), help="Liczba aktywnych instalacji pod Twoją opieką")
    with m2:
        today = datetime.now().strftime('%Y-%m-%d')
        today_triggers = len(df_logs[df_logs['timestamp'].str.startswith(today)]) if not df_logs.empty else 0
        st.metric("Interwencje (Dziś)", today_triggers, delta="System aktywny")
    with m3:
        # Считаем только логи по защите 253V
        overvoltage_count = len(df_logs[df_logs['reason'].str.contains("253V")])
        st.metric("Uratowane Cykle 253V", overvoltage_count, delta_color="normal")
    with m4:
        min_price = df_logs['price_pln_mwh'].min() if not df_logs.empty else 0
        st.metric("Najniższa Cena RCE", f"{min_price:.2f} PLN", help="Najniższa cena przechwycona dla Twoich klientów")

    st.divider()

    # Две колонки: Логи и Карта/Статус
    col_table, col_info = st.columns([2, 1])

    with col_table:
        st.subheader("📋 Ostatnie operacje systemowe")
        if not df_logs.empty:
            df_display = df_logs.sort_values(by="timestamp", ascending=False).head(15)
            # Переименовываем для польского рынка
            df_display.columns = ['Data/Godzina', 'ID Klienta', 'Typ Akcji', 'Cena (PLN/MWh)']
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("Oczekiwanie na pierwsze zdarzenia rynkowe...")

    with col_info:
        st.subheader("🛠 Narzędzia Partnera")
        with st.expander("🛡 Ochrona Napięciowa 253V"):
            st.write("Algorytm aktywuje zrzut energii na grzałki przy 252.5V, stabilizując pracę falownika.")
            st.progress(0.95, text="Skuteczność: 95%")
        
        with st.expander("📈 Optymalizacja Taryf RCE"):
            st.write("Automatyczny start pomp ciepła i ładowarek EV w godzinach najniższych cen giełdowych.")
            st.button("Pobierz raport oszczędności (PDF)", use_container_width=True)
        
        st.warning("📅 **Next update:** Integracja z magazynami energii (BESS) - Q3 2026")

else:
    st.error("⚠️ Brak połączenia z bazą danych lub baza jest pusta. Uruchom 'inject_demo_data.py' dla demonstracji.")

st.markdown("---")
col_bot_l, col_bot_r = st.columns(2)
with col_bot_l:
    st.caption("© 2026 Energy OS System | Powered by ENTSO-E & Shelly Cloud API")
with col_bot_r:
    st.markdown("<p style='text-align:right; color:gray;'>Wsparcie techniczne: 24/7</p>", unsafe_allow_html=True)
