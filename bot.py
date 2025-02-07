import requests
import schedule
import time

# Функция для получения курса USD/KZT
def get_usd_kzt():
    url = "https://api.exchangerate-api.com/v4/latest/USD"  # Замени на реальный API
    response = requests.get(url)
    data = response.json()
    rate = data['rates']['KZT']
    print(f"USD/KZT: {rate}")

# Функция для получения курса EUR/KZT
def get_eur_kzt():
    url = "https://api.exchangerate-api.com/v4/latest/EUR"  # Замени на реальный API
    response = requests.get(url)
    data = response.json()
    rate = data['rates']['KZT']
    print(f"EUR/KZT: {rate}")

# Функция для получения курса BTC/USD
def get_btc_usd():
    url = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
    response = requests.get(url)
    data = response.json()
    rate = data['bpi']['USD']['rate']
    print(f"BTC/USD: {rate}")

# Запуск задач по расписанию
schedule.every(1).minutes.do(get_usd_kzt)
schedule.every(1).minutes.do(get_eur_kzt)
schedule.every(1).minutes.do(get_btc_usd)

# Бесконечный цикл для выполнения задач
while True:
    schedule.run_pending()
    time.sleep(1)