import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

# Загружаем токен и URL webhook
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN:
    raise ValueError("TOKEN не найден! Убедитесь, что он добавлен в переменные окружения.")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не указан! Добавьте его в переменные окружения.")

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаём Telegram Bot
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context) -> None:
    await update.message.reply_text("Бот запущен!")

application.add_handler(CommandHandler("start", start))

# Flask-сервер
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST"])
async def webhook():
    json_update = request.get_json()
    logger.info(f"Получено обновление: {json_update}")

    update = Update.de_json(json_update, application.bot)
    await application.process_update(update)

    return "ok", 200

async def main():
    await application.initialize()
    await application.bot.set_webhook(WEBHOOK_URL + "/webhook")
    logger.info("Webhook установлен!")

if __name__ == "__main__":
    asyncio.run(main())  # Асинхронный запуск бота
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)), use_reloader=False)
