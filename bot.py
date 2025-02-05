import asyncio
import logging
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
    await update.message.reply_text("Привет! Я работаю автономно без Flask!")

# Основная функция запуска
async def main():
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота в режиме polling
    print("Бот запущен и ожидает команды...")
    await application.run_polling()

# Запускаем event loop для Render
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
