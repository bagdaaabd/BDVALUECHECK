import os
import time
import requests
import logging
from telegram import Bot

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Токен бота из переменной окружения
API_KEY = os.getenv("API_KEY")      # API-ключ из переменной окружения

# Проверяем, что переменные загружены
if not BOT_TOKEN or not API_KEY:
    raise ValueError(
        "Ошибка: Токен бота или API-ключ не найдены. "
        "Проверьте переменные окружения BOT_TOKEN и API_KEY!"
    )

# Инициализация бота
bot = Bot(token=BOT_TOKEN)

# ID чатов (замените на свои)
CHAT_IDS = ["-1002174956701", "-1002291124169"]  # ID ваших групп

# URL API для курсов валют
EXCHANGE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"

def get_exchange_rates():
    """Получает актуальные курсы валют."""
    try:
        response = requests.get(EXCHANGE_URL)
        data = response.json()
        
        if response.status_code != 200 or "conversion_rates" not in data:
            logger.error(f"Ошибка API: {data}. Статус код: {response.status_code}")
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

    text = "💱 *Актуальные курсы валют и криптовалют*:\n\n"

    if rates["USD/KZT"] is not None:
        text += f"🇺🇸 1 USD = {rates['USD/KZT']:.2f} KZT\n"
    else:
        text += "🇺🇸 1 USD = ❌ (нет данных)\n"

    if rates["EUR/KZT"] is not None:
        text += f"🇪🇺 1 EUR = {rates['EUR/KZT']:.2f} KZT\n"
    else:
        text += "🇪🇺 1 EUR = ❌ (нет данных)\n"

    if rates["BTC/USD"] is not None:
        text += f"₿ 1 BTC = {rates['BTC/USD']:.2f} USD\n"
    else:
        text += "₿ 1 BTC = ❌ (нет данных)\n"

    if rates["ETH/USD"] is not None:
        text += f"⛏ 1 ETH = {rates['ETH/USD']:.2f} USD\n"
    else:
        text += "⛏ 1 ETH = ❌ (нет данных)\n"

    for chat_id in CHAT_IDS:
        try:
            chat = bot.get_chat(chat_id)
            pinned_message = chat.pinned_message

            if pinned_message:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=pinned_message.message_id,
                    text=text,
                    parse_mode="Markdown",
                )
                logger.info(f"Сообщение в чате {chat_id} обновлено.")
            else:
                sent_message = bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode="Markdown",
                )
                bot.pin_chat_message(
                    chat_id=chat_id,
                    message_id=sent_message.message_id,
                )
                logger.info(f"Новое сообщение в чате {chat_id} отправлено и закреплено.")
        except Exception as e:
            logger.error(f"Ошибка при обновлении сообщения в {chat_id}: {e}")

if __name__ == "__main__":
    logger.info("Бот запущен.")
    while True:
        try:
            update_pinned_message()
        except Exception as e:
            logger.error(f"Ошибка в основном цикле: {e}")
        time.sleep(600)  # Обновление каждые 10 минут
