import logging
import os
import asyncio
import requests
import threading
from telegram import Bot
from dotenv import load_dotenv
from flask import Flask

# Загружаем переменные окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS", "").split(",")  # Список ID чатов
EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
CRYPTO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Проверяем токен перед запуском
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден! Проверьте переменные окружения.")

bot = Bot(token=TELEGRAM_TOKEN)

def get_exchange_rates():
    """Получает текущие курсы USD/KZT и EUR/KZT"""
    try:
        response = requests.get(EXCHANGE_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "rates" not in data:
            raise ValueError("Некорректный ответ API")

        usd_kzt = data["rates"].get("KZT", "N/A")
        eur_usd = data["rates"].get("EUR", "N/A")
        eur_kzt = usd_kzt * eur_usd if eur_usd != "N/A" and usd_kzt != "N/A" else "N/A"
        return usd_kzt, eur_kzt

    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
        return "N/A", "N/A"

def get_bitcoin_price():
    """Получает текущую цену биткоина в евро"""
    try:
        response = requests.get(CRYPTO_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        btc_eur = data.get("bitcoin", {}).get("eur", "N/A")
        return btc_eur

    except Exception as e:
        logger.error(f"Ошибка при получении цены биткоина: {e}")
        return "N/A"

async def update_pinned_message():
    """Обновляет закрепленное сообщение с актуальными курсами"""
    while True:
        usd_kzt, eur_kzt = get_exchange_rates()
        btc_eur = get_bitcoin_price()
        message_text = (
            f"💰 Актуальные курсы:\n"
            f"🇺🇸 USD/KZT: {usd_kzt}\n"
            f"🇪🇺 EUR/KZT: {eur_kzt}\n"
            f"₿ BTC/EUR: {btc_eur}"
        )

        for chat_id in CHAT_IDS:
            try:
                chat = await bot.get_chat(chat_id)
                pinned_msg = chat.pinned_message

                if pinned_msg:
                    await bot.edit_message_text(chat_id=chat_id, message_id=pinned_msg.message_id, text=message_text)
                else:
                    sent_msg = await bot.send_message(chat_id=chat_id, text=message_text)
                    await bot.pin_chat_message(chat_id=chat_id, message_id=sent_msg.message_id)

                logger.info(f"Сообщение обновлено в чате {chat_id}")
            except Exception as e:
                logger.error(f"Ошибка при обновлении сообщения в {chat_id}: {e}")

        await asyncio.sleep(600)  # Обновление каждые 10 минут

async def main():
    logger.info("Бот запущен!")
    await update_pinned_message()

# Запуск Flask-сервера в отдельном потоке
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
