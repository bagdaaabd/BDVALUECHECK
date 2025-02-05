import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Логирование (отображение ошибок)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Твой токен бота (замени на свой)
TOKEN = "8034613028:AAFf9SsJF5P1xgvPTO7vlltUKs8CEP7bToo"

# Функция обработки команды /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привет! Я работаю без Flask и webhooks.")

# Основная асинхронная функция
async def main():
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота в режиме polling
    await application.run_polling()

# Запускаем event loop правильно
if __name__ == "__main__":
    asyncio.run(main())
