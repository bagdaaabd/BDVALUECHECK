import os
import time
import requests
import logging
from telegram import Bot
from dotenv import load_dotenv

# Удаляем load_dotenv(), так как Render загружает переменные автоматически

# Загружаем переменные окружения
BOT_TOKEN = os.getenv("8034613028:AAFbmNg73gbhRIXpSlzGLG1rgMk29i8c0Ws")
API_KEY = os.getenv("80312c8d3cb3d0a7add04a6a")

# Проверяем, что переменные загружены
if not BOT_TOKEN or not API_KEY:
    raise ValueError("Ошибка: Токен бота или API-ключ не найдены. Проверьте переменные окружения!")

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)

# ID чатов (замени на свои)
CHAT_IDS = ["-1001234567890", "-1009876543210"]  # ID твоих групп

# URL API для курсов валют
EXCHANGE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"

def get_exchange_rates():
    """Получает актуальные курсы валют."""
    try:
        response = requests.get(EXCHANGE_URL)
        data = response.json()
        
        if response.status_code != 200 or "conversion_rates" not in data:
            logger.error(f"Ошибка API: {data}")
            return None

        rates = data["conversion_rates"]
        return {
            "USD/KZT": rates.get("KZT"),
            "EUR/KZT": rates.get("KZT") / rates.get("EUR") if rates.get("EUR") else None,
            "BTC/USD": get_crypto_price("BTC"),
            "ETH/USD": get_crypto_price("ETH"),
        }
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
        return None

def get_crypto_price(symbol):
    """Получает курс криптовалюты (BTC/USD, ETH/USD)."""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        return data[symbol.lower()]["usd"] if symbol.lower() in data else None
    except Exception as e:
        logger.error(f"Ошибка при получении курса {symbol}: {e}")
        return None

def update_pinned_message():
    """Обновляет закреплённое сообщение в группах с актуальными курсами."""
    rates = get_exchange_rates()
    if not rates:
        logger.error("Не удалось получить курсы, сообщение не обновлено.")
        return
    
    text = (
        f"💱 *Актуальные курсы валют и криптовалют*:\n\n"
        f"🇺🇸 1 USD = {rates['USD/KZT']:.2f} KZT\n"
        f"🇪🇺 1 EUR = {rates['EUR/KZT']:.2f} KZT\n"
        f"₿ 1 BTC = {rates['BTC/USD']:.2f} USD\n"
        f"⛏ 1 ETH = {rates['ETH/USD']:.2f} USD\n"
    )

    for chat_id in CHAT_IDS:
        try:
            messages = bot.get_chat(chat_id).pinned_message
            if messages:
                bot.edit_message_text(chat_id=chat_id, message_id=messages.message_id, text=text, parse_mode="Markdown")
            else:
                sent_message = bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
                bot.pin_chat_message(chat_id=chat_id, message_id=sent_message.message_id)
        except Exception as e:
            logger.error(f"Ошибка при обновлении сообщения в {chat_id}: {e}")

if __name__ == "__main__":
    while True:
        update_pinned_message()
        time.sleep(600)  # Обновление каждые 10 минут
