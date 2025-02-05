import os
import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TOKEN = os.getenv("BOT_TOKEN")  # Получаем токен из переменной окружения

# Создаём Flask-сервер
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

# Функция для обработки команды /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Я бот для проверки курсов валют.")

# Создаём бота
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))

# Функция для запуска бота в отдельном потоке
def run_bot():
    loop = asyncio.new_event_loop()  # Создаём новый event loop
    asyncio.set_event_loop(loop)  # Устанавливаем его как текущий
    loop.run_until_complete(application.run_polling())  # Запускаем бота

# Запускаем бота в отдельном потоке
threading.Thread(target=run_bot, daemon=True).start()

# Запускаем Flask-сервер
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
