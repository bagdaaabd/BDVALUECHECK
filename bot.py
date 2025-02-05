import logging
import os
import asyncio
import requests
from telegram import Bot
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS", "").split(",")  # Список ID чатов
API_URL = "https://api.exchangerate-api.com/v4/latest/USD"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Проверяем токен перед запуском
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден! Проверьте переменные окружения.")

bot = Bot(token=TELEGRAM_TOKEN)

def get_exchange_rates():
    """Получает текущие курсы валют USD/KZT и EUR/KZT"""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "rates" not in data:
            raise ValueError("Некорректный ответ API")

        usd_kzt = data["rates"].get("KZT", "N/A")
        eur_kzt = data["rates"].get("EUR", "N/A")
        return usd_kzt, eur_kzt

    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
        return "N/A", "N/A"

async def update_pinned_message():
    """Обновляет закрепленное сообщение с актуальными курсами"""
    while True:
        usd_kzt, eur_kzt = get_exchange_rates()
        message_text = f"💰 Актуальные курсы:\n🇺🇸 USD/KZT: {usd_kzt}\n🇪🇺 EUR/KZT: {eur_kzt}"

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

if __name__ == "__main__":
    asyncio.run(main())
import flask

app = flask.Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

if __name__ == "__main__":
    import threading
    server = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000))
    server.start()
    asyncio.run(main())
