import os
import logging
import requests
import asyncio
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("EXCHANGE_API_KEY")
CHAT_IDS = [-1002174956701, -1002291124169]

if not TOKEN or not API_KEY:
    raise ValueError("Ошибка: Токен бота или API-ключ не найдены. Проверьте переменные окружения!")

# Логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Application.builder().token(TOKEN).build()

# Функция получения курса валют
def get_exchange_rates():
    url = f"https://api.exchangerate-api.com/v4/latest/USD?apikey={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        usd_kzt = data["rates"]["KZT"]
        eur_kzt = data["rates"]["KZT"] / data["rates"]["EUR"]
    except Exception as e:
        logging.error(f"Ошибка получения курса валют: {e}")
        usd_kzt, eur_kzt = "Ошибка", "Ошибка"

    return usd_kzt, eur_kzt

# Функция получения курса криптовалют
def get_crypto_rates():
    url = f"https://api.cryptonator.com/api/ticker/btc-usd"
    try:
        response = requests.get(url)
        btc_usd = response.json()["ticker"]["price"]
    except Exception as e:
        logging.error(f"Ошибка получения курса BTC/USD: {e}")
        btc_usd = "Ошибка"

    url = f"https://api.cryptonator.com/api/ticker/eth-usd"
    try:
        response = requests.get(url)
        eth_usd = response.json()["ticker"]["price"]
    except Exception as e:
        logging.error(f"Ошибка получения курса ETH/USD: {e}")
        eth_usd = "Ошибка"

    return btc_usd, eth_usd

# Обновление закрепленного сообщения
async def update_pinned_message(context: ContextTypes.DEFAULT_TYPE):
    usd_kzt, eur_kzt = get_exchange_rates()
    btc_usd, eth_usd = get_crypto_rates()

    message = (
        f"📊 *Курсы валют и криптовалют*:\n"
        f"🇺🇸 1 USD = {usd_kzt} KZT\n"
        f"🇪🇺 1 EUR = {eur_kzt} KZT\n"
        f"🟠 1 BTC = {btc_usd} USD\n"
        f"🔵 1 ETH = {eth_usd} USD\n"
    )

    for chat_id in CHAT_IDS:
        try:
            bot = context.bot
            pinned_messages = await bot.get_chat(chat_id)
            if pinned_messages.pinned_message:
                await bot.edit_message_text(chat_id=chat_id, message_id=pinned_messages.pinned_message.message_id, text=message, parse_mode="Markdown")
            else:
                sent_message = await bot.send_message(chat_id, text=message, parse_mode="Markdown")
                await bot.pin_chat_message(chat_id, sent_message.message_id)
        except Exception as e:
            logging.error(f"Ошибка обновления закрепленного сообщения в чате {chat_id}: {e}")

# Команда /start
async def start(update, context):
    await update.message.reply_text("Привет! Я бот для обновления курса валют.")

app.add_handler(CommandHandler("start", start))

# Запускаем задачу автообновления сообщений
async def periodic_update():
    while True:
        await update_pinned_message(ContextTypes.DEFAULT_TYPE)
        await asyncio.sleep(600)  # 10 минут

if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()
    asyncio.run(periodic_update())
