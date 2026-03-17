import os
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz

# СТРАТЕГИЧЕСКИЙ СТЕК: ENTSO-E (Core Data) + NBP (Currency)
ENTSOE_API_KEY = os.getenv("ENTSOE_API_KEY")
DOMAIN_PL = "10YPL-AREA-----S"
ENDPOINT_ENTSOE = "https://web-api.tp.entsoe.eu/api"
ENDPOINT_NBP = "https://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json"

def get_pln_rate():
    """Извлекает актуальный курс EUR/PLN из API NBP. Ресурсная автономность."""
    try:
        response = requests.get(ENDPOINT_NBP, timeout=5)
        response.raise_for_status()
        return response.json()['rates'][0]['mid']
    except Exception as e:
        print(f"⚠️ Ошибка NBP: {e}. Дефолт: 4.3")
        return 4.3

def get_tomorrow_prices():
    """Запрос первичных данных RDN на завтрашний день."""
    tz = pytz.timezone('Europe/Warsaw')
    tomorrow = datetime.now(tz) + timedelta(days=1)
    
    # Формирование UTC окна запроса
    p_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
    p_end = (tomorrow + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)

    params = {
        'securityToken': ENTSOE_API_KEY,
        'documentType': 'A44',
        'in_Domain': DOMAIN_PL,
        'out_Domain': DOMAIN_PL,
        'periodStart': p_start.strftime('%Y%m%d%H00'),
        'periodEnd': p_end.strftime('%Y%m%d%H00')
    }

    print(f"📡 Запрос ENTSO-E: Польша (RDN) на {tomorrow.strftime('%Y-%m-%d')}")
    
    try:
        res = requests.get(ENDPOINT_ENTSOE, params=params, timeout=15)
        res.raise_for_status()
        return parse_entsoe_xml(res.text)
    except Exception as e:
        print(f"❌ Критический сбой API: {e}")
        return None

def parse_entsoe_xml(xml_data):
    """Парсинг с защитой от изменения схемы (Namespace) и поддержкой PT15M/PT60M."""
    root = ET.fromstring(xml_data)
    
    # Перехват системных ошибок биржи
    reason = root.find('.//Reason/text')
    if reason is not None:
        print(f"❌ ENTSO-E REJECT: {reason.text}")
        return None

    # Динамический неймспейс
    ns_match = re.match(r'\{(.*)\}', root.tag)
    ns = {'ns': ns_match.group(1)} if ns_match else {}
    
    # Проверка валюты
    cur_node = root.find('.//ns:currency_Unit.name', ns)
    currency = cur_node.text if cur_node is not None else "EUR"
    
    tz_pl = pytz.timezone('Europe/Warsaw')
    prices = []

    # Сбор данных по всем TimeSeries (защита от неполных блоков)
    for ts in root.findall('.//ns:TimeSeries', ns):
        period = ts.find('ns:Period', ns)
        if period is None: continue
        
        res_type = period.find('ns:resolution', ns).text
        start_str = period.find('ns:timeInterval/ns:start', ns).text
        curr_utc = datetime.strptime(start_str, '%Y-%m-%dT%H:%MZ').replace(tzinfo=pytz.utc)
        
        for point in period.findall('ns:Point', ns):
            val = float(point.find('ns:price.amount', ns).text)
            prices.append({
                'ts': curr_utc.astimezone(tz_pl),
                'price_raw': val,
                'currency': currency
            })
            # Сдвиг времени согласно резолюции рынка (15 мин или 1 час)
            curr_utc += timedelta(minutes=15) if res_type == 'PT15M' else timedelta(hours=1)

    return sorted(prices, key=lambda x: x['ts'])

def evaluate_market_state(data, threshold_pln=0.0):
    """Конвертация в PLN и выявление триггеров для M2M автоматизации."""
    rate = get_pln_rate()
    print(f"💰 Курс NBP: 1 EUR = {rate} PLN")
    print(f"🧠 Анализ {len(data)} временных слотов...")
    
    anomalies = []
    for slot in data:
        # Конвертация: (EUR/MWh * Rate) / 10 = gr/kWh (или /1000 для PLN/kWh)
        # Для удобства триггера считаем в PLN/MWh
        price_pln_mwh = slot['price_raw'] * rate
        
        if price_pln_mwh <= threshold_pln:
            anomalies.append({
                'time': slot['ts'].strftime('%H:%M'),
                'price': round(price_pln_mwh, 2)
            })

    if anomalies:
        print(f"🔥 ТРИГГЕР: Найдено {len(anomalies)} интервалов ниже порога {threshold_pln} PLN/MWh")
        for a in anomalies:
            print(f" -> [{a['time']}] Цена: {a['price']} PLN/MWh")
    else:
        print("✅ Рынок стабилен. Сигналов для включения нагрузки нет.")
    
    return anomalies

if __name__ == "__main__":
    market_data = get_tomorrow_prices()
    if market_data:
        # Тестовый порог: 200 PLN/MWh (около 20 gr/kWh), для боевого режима ставь 0.0
        evaluate_market_state(market_data, threshold_pln=200.0)