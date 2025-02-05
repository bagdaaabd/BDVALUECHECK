import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Загружаем токен из переменных окружения
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN не найден! Убедитесь, что он добавлен в переменные окружения.")

# Загружаем URL webhook из переменных окружения
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не указан! Добавьте его в переменные окружения.")

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаём Telegram Bot
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Бот запущен!')

application.add_handler(CommandHandler("start", start))

# Flask-сервер для webhook
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    # Вместо application.create_task(...) используем asyncio.run
    asyncio.run(application.process_update(update))
    return "ok", 200

if __name__ == "__main__":
    # Выводим переменные для отладки
    print(f"TOKEN: {'OK' if TOKEN else 'NOT FOUND'}")
    print(f"WEBHOOK_URL: {WEBHOOK_URL}")

    # Устанавливаем webhook перед запуском сервера
    async def set_webhook():
        await application.bot.set_webhook(WEBHOOK_URL + "/webhook")

    asyncio.run(set_webhook())

    # Запускаем Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), use_reloader=False)
