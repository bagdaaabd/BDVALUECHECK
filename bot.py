import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Твой токен бота
TOKEN = "8034613028:AAFf9SsJF5P1xgvPTO7vlltUKs8CEP7bToo"

# Функция обработки команды /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привет! Я работаю автономно!")

# Основная функция бота
def run_bot():
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота в режиме polling
    print("Бот запущен и работает...")
   import threading
import asyncio

def run_bot():
    loop = asyncio.new_event_loop()  # Создаём новый event loop
    asyncio.set_event_loop(loop)  # Устанавливаем его как текущий
    loop.run_until_complete(application.run_polling())  # Запускаем бота

threading.Thread(target=run_bot, daemon=True).start()  # Запускаем в отдельном потоке

# Запуск через event loop
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_in_executor(None, run_bot)
    loop.run_forever()
