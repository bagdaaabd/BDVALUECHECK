import asyncio  # 🔥 Добавляем поддержку асинхронного кода

async def update_pinned_message():
    """Обновляет закреплённое сообщение в группах с актуальными курсами."""
    rates = get_exchange_rates()
    if not rates:
        logger.error("Не удалось получить курсы, сообщение не обновлено.")
        return

    text = "💱 *Актуальные курсы валют и криптовалют*:\n\n"

    if rates["USD/KZT"] is not None:
        text += f"🇺🇸 1 USD = {rates['USD/KZT']:.2f} KZT\n"
    else:
        text += "🇺🇸 1 USD = ❌ (нет данных)\n"

    if rates["EUR/KZT"] is not None:
        text += f"🇪🇺 1 EUR = {rates['EUR/KZT']:.2f} KZT\n"
    else:
        text += "🇪🇺 1 EUR = ❌ (нет данных)\n"

    if rates["BTC/USD"] is not None:
        text += f"₿ 1 BTC = {rates['BTC/USD']:.2f} USD\n"
    else:
        text += "₿ 1 BTC = ❌ (нет данных)\n"

    if rates["ETH/USD"] is not None:
        text += f"⛏ 1 ETH = {rates['ETH/USD']:.2f} USD\n"
    else:
        text += "⛏ 1 ETH = ❌ (нет данных)\n"

    for chat_id in CHAT_IDS:
        try:
            chat = await bot.get_chat(chat_id)  # 🔥 Добавляем await
            pinned_message = chat.pinned_message

            if pinned_message:
                await bot.edit_message_text(  # 🔥 Добавляем await
                    chat_id=chat_id,
                    message_id=pinned_message.message_id,
                    text=text,
                    parse_mode="Markdown",
                )
                logger.info(f"Сообщение в чате {chat_id} обновлено.")
            else:
                sent_message = await bot.send_message(  # 🔥 Добавляем await
                    chat_id=chat_id,
                    text=text,
                    parse_mode="Markdown",
                )
                await bot.pin_chat_message(  # 🔥 Добавляем await
                    chat_id=chat_id,
                    message_id=sent_message.message_id,
                )
                logger.info(f"Новое сообщение в чате {chat_id} отправлено и закреплено.")
        except Exception as e:
            logger.error(f"Ошибка при обновлении сообщения в {chat_id}: {e}")

async def main():
    """Основной цикл бота."""
    logger.info("Бот запущен.")
    while True:
        try:
            await update_pinned_message()  # 🔥 Теперь вызываем с await
        except Exception as e:
            logger.error(f"Ошибка в основном цикле: {e}")
        await asyncio.sleep(600)  # 🔥 Используем await вместо time.sleep

if __name__ == "__main__":
    asyncio.run(main())  # 🔥 Запускаем асинхронную функцию
