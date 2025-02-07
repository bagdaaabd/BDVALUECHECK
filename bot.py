import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

# Загружаем токен и URL webhook
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

if not TOKEN:
    raise ValueError("❌ TOKEN не найден! Убедитесь, что он добавлен в переменные окружения.")
if not WEBHOOK_URL:
    raise ValueError("❌ WEBHOOK_URL не указан! Добавьте его в переменные окружения.")

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаём Telegram Bot
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context) -> None:
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
    asyncio.run(application.process_update(update))  # Запускаем обработку асинхронно

    return "ok", 200

async def set_webhook():
    """Функция устанавливает webhook"""
    await application.bot.set_webhook(WEBHOOK_URL + "/webhook")
    logger.info(f"✅ Webhook установлен: {WEBHOOK_URL}/webhook")

async def send_startup_message():
    """Отправка тестового сообщения в группы при запуске"""
    chat_ids = [-1002291124169, -1002174956701]
    for chat_id in chat_ids:
        try:
            await application.bot.send_message(chat_id=chat_id, text="🚀 Бот запущен и работает!")
            logger.info(f"📤 Сообщение отправлено в группу {chat_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в {chat_id}: {e}")

async def main():
    await application.initialize()
    await set_webhook()
    await application.start()
    await send_startup_message()  # Отправляем тестовое сообщение в группы

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())  # Запускаем бота в асинхронном режиме
    app.run(host="0.0.0.0", port=PORT, use_reloader=False)  # Запускаем Flask
