import logging
import os
import asyncio
import requests
import threading
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv
from flask import Flask

# Загружаем переменные окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS", "").split(",")
EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
CRYPTO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,tether,binancecoin&vs_currencies=usd"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

async def get_exchange_rates():
    """Получает курсы мировых валют."""
    try:
        response = requests.get(EXCHANGE_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["rates"]
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
        return {}

async def get_crypto_prices():
    """Получает цены основных криптовалют."""
    try:
        response = requests.get(CRYPTO_API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка при получении данных о криптовалютах: {e}")
        return {}

async def update_pinned_message():
    """Обновляет закрепленное сообщение с актуальными курсами."""
    while True:
        rates = await get_exchange_rates()
        crypto = await get_crypto_prices()

        message_text = f"💰 Актуальные курсы:\n"
        message_text += f"🇺🇸 USD/KZT: {rates.get('KZT', 'N/A')}\n"
        message_text += f"🇪🇺 EUR/KZT: {rates.get('KZT', 'N/A') * rates.get('EUR', 'N/A') if 'KZT' in rates and 'EUR' in rates else 'N/A'}\n"
        message_text += f"₿ BTC/USD: {crypto.get('bitcoin', {}).get('usd', 'N/A')}\n"
        message_text += f"Ξ ETH/USD: {crypto.get('ethereum', {}).get('usd', 'N/A')}\n"
        message_text += f"🪙 USDT/USD: {crypto.get('tether', {}).get('usd', 'N/A')}\n"

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

        await asyncio.sleep(600)

async def start(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    await update.message.reply_text("Привет! Я бот для отслеживания курсов валют и криптовалют.")

async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    threading.Thread(target=run_flask, daemon=True).start()
    await update_pinned_message()
    await application.run_polling()

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    asyncio.run(main())
@app.route('/', methods=['GET'])
def home():
    return "Bot is running and ready!", 200
