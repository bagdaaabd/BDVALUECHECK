import os
import logging
import asyncio
import threading
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Загружаем токен и URL webhook из переменных окружения
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN:
    raise ValueError("TOKEN не найден! Убедитесь, что он добавлен в переменные окружения.")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не указан! Добавьте его в переменные окружения.")

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Создаём Telegram Bot
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Бот запущен!")

application.add_handler(CommandHandler("start", start))

# Flask-сервер для webhook
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        json_update = request.get_json()
        logger.info(f"Получено обновление: {json_update}")

        if not json_update:
            return "No update data", 400  # Ошибка, если JSON пустой

        update = Update.de_json(json_update, application.bot)
        future = asyncio.run_coroutine_threadsafe(application.process_update(update), event_loop)
        future.result()  # Ждём завершения обработки

        return "ok", 200

    except Exception as e:
        logger.error(f"Ошибка в webhook: {e}")
        return "Internal Server Error", 500


# Глобальный event loop для Telegram
event_loop = asyncio.new_event_loop()

def start_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Запуск event loop в отдельном потоке
threading.Thread(target=start_loop, args=(event_loop,), daemon=True).start()

async def main_setup():
    await application.initialize()
    await application.bot.set_webhook(WEBHOOK_URL + "/webhook")
    logger.info("Webhook установлен!")

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main_setup())  # Запускаем асинхронную настройку корректно
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), use_reloader=False)
