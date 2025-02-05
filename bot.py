import logging
import asyncio
import os
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные окружения (лучше использовать вместо открытого API-ключа)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Токен бота
API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")  # API-ключ для валют
CHAT_IDS = ["-1002174956701", "-1002291124169"]  # ID групп

# URL для получения курсов
CURRENCY_API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
CRYPTO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"

# Функция получения курсов валют
async def get_currency_data():
    usd_kzt, eur_kzt, btc_usd, eth_usd = "Ошибка", "Ошибка", "Ошибка", "Ошибка"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(CURRENCY_API_URL, timeout=10)
            crypto_response = await client.get(CRYPTO_API_URL, timeout=10)

            if response.status_code == 200:
                data = response.json()
                usd_kzt = round(data["conversion_rates"].get("KZT", 0), 2)
                eur_usd = data["conversion_rates"].get("EUR", 0)
                eur_kzt = round(usd_kzt * eur_usd, 2)
            else:
                logger.error(f"Ошибка API валют: {response.status_code}")

            if crypto_response.status_code == 200:
                crypto_data = crypto_response.json()
                btc_usd = round(crypto_data.get("bitcoin", {}).get("usd", 0), 2)
                eth_usd = round(crypto_data.get("ethereum", {}).get("usd", 0), 2)
            else:
                logger.error(f"Ошибка API криптовалют: {crypto_response.status_code}")

        except Exception as e:
            logger.error(f"Ошибка при получении данных: {e}")

    return usd_kzt, eur_kzt, btc_usd, eth_usd

# Функция форматирования сообщения
def format_message(usd_kzt, eur_kzt, btc_usd, eth_usd):
    return (
        f"📢 Актуальные курсы валют и криптовалют:\n\n"
        f"💵 USD/KZT: {usd_kzt} ₸\n"
        f"💶 EUR/KZT: {eur_kzt} ₸\n\n"
        f"🌐 Криптовалюты:\n"
        f"₿ BTC/USD: {btc_usd} $\n"
        f"⚡ ETH/USD: {eth_usd} $\n\n"
        f"🔄 Обновлено автоматически каждые 10 минут"
    )

# Отправка или обновление закрепленного сообщения в группах
async def update_pinned_message(app: Application):
    while True:
        usd_kzt, eur_kzt, btc_usd, eth_usd = await get_currency_data()
        message_text = format_message(usd_kzt, eur_kzt, btc_usd, eth_usd)
        
        for chat_id in CHAT_IDS:
            try:
                sent_message = await app.bot.send_message(chat_id, text=message_text)
                await app.bot.pin_chat_message(chat_id, sent_message.message_id)
                logger.info(f"Сообщение закреплено в чате {chat_id}")
            except Exception as e:
                logger.error(f"Ошибка при отправке в чат {chat_id}: {e}")

        await asyncio.sleep(600)  # Ждем 10 минут

# Команда /rate
async def rate(update: Update, context: CallbackContext) -> None:
    usd_kzt, eur_kzt, btc_usd, eth_usd = await get_currency_data()
    message_text = format_message(usd_kzt, eur_kzt, btc_usd, eth_usd)
    await update.message.reply_text(message_text)

# Основная функция
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("rate", rate))

    # Запуск фонового обновления сообщений
    loop = asyncio.get_event_loop()
    loop.create_task(update_pinned_message(app))

    logger.info("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
