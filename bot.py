import os
import logging
import asyncio
import httpx
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler
import uvicorn  # Используем uvicorn для ASGI сервера

# Настройки
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))
CHAT_IDS = [-1002291124169, -1002174956701]  # ID групп

if not TOKEN:
    raise ValueError("❌ TOKEN не найден! Убедитесь, что он добавлен в переменные окружения.")
if not WEBHOOK_URL:
    raise ValueError("❌ WEBHOOK_URL не указан! Добавьте его в переменные окружения.")

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# API для курсов валют
CURRENCY_API_URL = "https://api.apilayer.com/currency_data/live?source=USD&currencies=KZT,EUR&apikey=SC86xx0kCQ90R0a9Wi7oGU4zvqmy4Qnq"
CRYPTO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"

# Функция для получения курсов
async def fetch_rates():
    async with httpx.AsyncClient() as client:
        currency_response = await client.get(CURRENCY_API_URL)
        crypto_response = await client.get(CRYPTO_API_URL)
    
    if currency_response.status_code == 200 and crypto_response.status_code == 200:
        currency_data = currency_response.json()
        crypto_data = crypto_response.json()
        
        usd_kzt = currency_data["quotes"].get("USDKZT", "N/A")
        eur_usd = currency_data["quotes"].get("USDEUR", 1)
        eur_kzt = usd_kzt / eur_usd if eur_usd != 0 else "N/A"
        btc_usd = crypto_data["bitcoin"]["usd"]
        eth_usd = crypto_data["ethereum"]["usd"]
        
        logger.info(f"📊 Курс валют: {currency_data}")
        logger.info(f"🪙 Курс криптовалют: {crypto_data}")
        
        return (f"💰 *Актуальные курсы валют и криптовалют:*\n\n"
                f"🇺🇸 1 USD = {usd_kzt:.2f} KZT\n"
                f"🇪🇺 1 EUR = {eur_kzt:.2f} KZT\n"
                f"🟠 1 BTC = ${btc_usd:.2f}\n"
                f"💎 1 ETH = ${eth_usd:.2f}")
    else:
        return "⚠️ Ошибка получения данных о курсах."

# Функция для обновления закрепленного сообщения
async def update_pinned_message():
    text = await fetch_rates()
    for chat_id in CHAT_IDS:
        message = await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
        await bot.pin_chat_message(chat_id=chat_id, message_id=message.message_id)
        logger.info(f"📌 Закреплено новое сообщение в {chat_id}, ID: {message.message_id}")

# Функция для старта бота
async def start(update: Update, context):
    await update.message.reply_text("✅ Бот запущен и работает!")

application.add_handler(CommandHandler("start", start))

# Flask-сервер
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    json_update = request.get_json()
    logger.info(f"📩 Получено обновление: {json_update}")
    update = Update.de_json(json_update, application.bot)
    application.process_update(update)
    return "ok", 200

# Устанавливаем Webhook
async def set_webhook():
    await application.bot.set_webhook(WEBHOOK_URL + "/webhook")
    logger.info(f"✅ Webhook установлен: {WEBHOOK_URL}/webhook")

# Функция для периодического обновления
async def periodic_update():
    while True:
        await update_pinned_message()
        await asyncio.sleep(600)  # Каждые 10 минут

# Основная функция
async def main():
    await application.initialize()
    await set_webhook()
    asyncio.create_task(periodic_update())  # Запускаем обновление курсов в фоне
    await application.start()  # Запускаем обработку вебхуков

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())  # Запускаем бота в фоне
    uvicorn.run(app, host="0.0.0.0", port=PORT)  # Запускаем Flask через Uvicorn
