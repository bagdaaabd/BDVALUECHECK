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

# ID групп
GROUP_IDS = [-1002291124169, -1002174956701]
pinned_messages = {}  # Храним message_id закрепленных сообщений

async def start(update: Update, context) -> None:
    await update.message.reply_text("✅ Бот запущен и работает!")

application.add_handler(CommandHandler("start", start))

# Функция для обновления курса
async def update_pinned_message():
    global pinned_messages
    new_text = "🔄 Актуальные курсы валют:\nUSD/KZT: 450.5\nEUR/KZT: 495.3\nBTC/USD: 43000\nETH/USD: 2500"

    for chat_id in GROUP_IDS:
        try:
            # Получаем текущее закрепленное сообщение
            pinned_message = await application.bot.get_chat(chat_id)
            message_id = pinned_message.pinned_message.message_id if pinned_message.pinned_message else None

            if message_id:
                # Если закрепленное сообщение есть, обновляем
                logger.info(f"🔄 Обновляем закрепленное сообщение в {chat_id}, ID: {message_id}")
                await application.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text)
            else:
                # Если нет, создаем новое сообщение и закрепляем его
                sent_message = await application.bot.send_message(chat_id=chat_id, text=new_text)
                await application.bot.pin_chat_message(chat_id=chat_id, message_id=sent_message.message_id)
                pinned_messages[chat_id] = sent_message.message_id
                logger.info(f"📌 Закреплено новое сообщение в {chat_id}, ID: {sent_message.message_id}")

        except Exception as e:
            logger.error(f"⚠️ Ошибка обновления в {chat_id}: {e}")

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
    asyncio.run(application.process_update(update))

    return "ok", 200

async def set_webhook():
    """Функция устанавливает webhook"""
    await application.bot.set_webhook(WEBHOOK_URL + "/webhook")
    logger.info(f"✅ Webhook установлен: {WEBHOOK_URL}/webhook")

async def main():
    await application.initialize()
    await set_webhook()
    await application.start()

    # Запуск обновления курсов каждые 10 минут
    while True:
        await update_pinned_message()
        await asyncio.sleep(600)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())  
    app.run(host="0.0.0.0", port=PORT, use_reloader=False)
