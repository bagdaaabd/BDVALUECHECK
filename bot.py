import requests
import schedule
import time
from telegram import Bot
from telegram.error import TelegramError

# Токен твоего бота
TELEGRAM_TOKEN = "8034613028:AAGSkyT7NDisVrBxaboV1uI9EQGoCTg7qeU"
# ID чата (можно получить через бота @userinfobot)
CHAT_ID = "-1002291124169","-1002174956701"

# Инициализация бота
bot = Bot(token=TELEGRAM_TOKEN)

# Переменная для хранения ID последнего сообщения
last_message_id = None

# Функция для получения курса USD/KZT
def get_usd_kzt():
    url = "https://api.exchangerate-api.com/v4/latest/USD"  # Замени на реальный API
    response = requests.get(url)
    data = response.json()
    rate = data['rates']['KZT']
    return f"USD/KZT: {rate}"

# Функция для получения курса EUR/KZT
def get_eur_kzt():
    url = "https://api.exchangerate-api.com/v4/latest/EUR"  # Замени на реальный API
    response = requests.get(url)
    data = response.json()
    rate = data['rates']['KZT']
    return f"EUR/KZT: {rate}"

# Функция для получения курса BTC/USD
def get_btc_usd():
    url = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
    response = requests.get(url)
    data = response.json()
    rate = data['bpi']['USD']['rate']
    return f"BTC/USD: {rate}"

# Функция для отправки и обновления сообщения
def update_rates():
    global last_message_id

    # Получаем актуальные курсы
    usd_kzt = get_usd_kzt()
    eur_kzt = get_eur_kzt()
    btc_usd = get_btc_usd()

    # Формируем сообщение
    message = f"📊 Актуальные курсы:\n{usd_kzt}\n{eur_kzt}\n{btc_usd}"

    try:
        if last_message_id:
            # Редактируем существующее сообщение
            bot.edit_message_text(chat_id=CHAT_ID, message_id=last_message_id, text=message)
        else:
            # Отправляем новое сообщение и сохраняем его ID
            sent_message = bot.send_message(chat_id=CHAT_ID, text=message)
            last_message_id = sent_message.message_id
    except TelegramError as e:
        print(f"Ошибка при отправке/редактировании сообщения: {e}")

# Запуск задачи по расписанию
schedule.every(1).minutes.do(update_rates)

# Бесконечный цикл для выполнения задач
while True:
    schedule.run_pending()
    time.sleep(1)
