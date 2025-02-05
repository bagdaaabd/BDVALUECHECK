import os
import logging
import threading
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TOKEN = os.getenv("8034613028:AAFf9SsJF5P1xgvPTO7vlltUKs8CEP7bToo")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Создаем приложение Telegram Bot
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Бот запущен!')

application.add_handler(CommandHandler("start", start))

def run_bot():
    # Запускаем polling в главном потоке
    application.run_polling()

# Flask-сервер
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

def run_flask():
    app.run(host="0.0.0.0", port=10000, use_reloader=False)

if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Запускаем бота в главном потоке
    run_bot()
