import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RCE Autopilot | B2B Panel", page_icon="⚡", layout="wide")



st.title("⚡️ Panel Instalatora: Zarządzanie Taryfami RCE")
st.markdown("""
**Zwiększ sprzedaż swoich instalacji PV.** Oferuj klientom ten system jako własny (White-Label). Algorytm automatycznie włącza pompy ciepła i bojlery Twoich klientów w godzinach ujemnych cen na giełdzie, skracając czas zwrotu z inwestycji (ROI).
""")

# Дальше идет твой код функции load_data() и колонок...

st.title("⚡️ Autopilot Taryf Dynamicznych (RCE)")
st.markdown("Monitorowanie giełdy ENTSO-E i automatyczne zarządzanie obciążeniami (Bojlery, Pompy Ciepła).")

# Подключение к базе (только чтение)
def load_data():
    conn = sqlite3.connect("triggers.db")
    # Логи срабатываний
    df_logs = pd.read_sql_query("SELECT timestamp, user_label, reason, price_pln_mwh FROM execution_logs", conn)
    # Активные клиенты
    df_users = pd.read_sql_query("SELECT user_label, threshold_pln_mwh FROM user_triggers WHERE is_active=1", conn)
    conn.close()
    return df_logs, df_users

try:
    df_logs, df_users = load_data()
    
    # Метрики для бизнеса
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Aktywne Obiekty", len(df_users))
    with col2:
        today = datetime.now().strftime('%Y-%m-%d')
        today_triggers = len(df_logs[df_logs['timestamp'].str.startswith(today)]) if not df_logs.empty else 0
        st.metric("Dzisiejsze Aktywacje (Tania Energia)", today_triggers)
    with col3:
        min_price = df_logs['price_pln_mwh'].min() if not df_logs.empty else 0
        st.metric("Najniższa przechwycona cena", f"{min_price:.2f} PLN")

    st.divider()

    # Таблица последних операций
    st.subheader("Ostatnie Interwencje Systemu")
    if not df_logs.empty:
        # Сортируем по убыванию (новые сверху)
        df_display = df_logs.sort_values(by="timestamp", ascending=False).head(10)
        df_display.columns = ['Data / Czas', 'ID Obiektu', 'Powód', 'Cena (PLN/MWh)']
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Brak danych operacyjnych. System oczekuje na anomalię rynkową.")

except Exception as e:
    st.error("Błąd połączenia z bazą danych operacyjnych.")

st.markdown("---")
st.caption("Gotowe rozwiązanie White-Label dla instalatorów PV. API Powered by ENTSO-E.")
