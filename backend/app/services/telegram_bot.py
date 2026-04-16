"""
Telegram bot service.
Handles /start <user_id> to link a user's Telegram account.
Started as a background task in main.py lifespan.
"""
import asyncio
import logging

logger = logging.getLogger(__name__)

_ptb_app = None


async def start_bot() -> None:
    from app.config import settings
    if not settings.telegram_bot_token:
        logger.info("TELEGRAM_BOT_TOKEN not set — bot disabled")
        return

    from telegram.ext import ApplicationBuilder, CommandHandler
    from telegram import Update
    from app.database import AsyncSessionLocal
    from app.models.user import User
    from sqlalchemy import select

    async def start_handler(update: Update, context) -> None:
        args = context.args
        chat_id = str(update.effective_chat.id)

        if not args:
            await update.message.reply_text(
                "👋 Привет!\n\n"
                "Для подключения уведомлений из HireFlow:\n"
                "1. Откройте профиль в приложении\n"
                "2. Нажмите «Подключить Telegram»\n"
                "3. Перейдите по сгенерированной ссылке"
            )
            return

        try:
            user_id = int(args[0])
        except ValueError:
            await update.message.reply_text("❌ Неверный формат ссылки.")
            return

        async with AsyncSessionLocal() as db:
            res = await db.execute(select(User).where(User.id == user_id))
            user = res.scalar_one_or_none()
            if not user:
                await update.message.reply_text("❌ Пользователь не найден.")
                return
            user.telegram_chat_id = chat_id
            await db.commit()

        await update.message.reply_text(
            "✅ Telegram подключён!\n\n"
            "Теперь вы будете получать уведомления из HireFlow:\n"
            "• Изменения статуса заявок\n"
            "• Назначенные интервью\n"
            "• Обновления запросов"
        )

    global _ptb_app
    _ptb_app = ApplicationBuilder().token(settings.telegram_bot_token).build()
    _ptb_app.add_handler(CommandHandler("start", start_handler))

    await _ptb_app.initialize()
    await _ptb_app.start()
    await _ptb_app.updater.start_polling(drop_pending_updates=True)
    logger.info("Telegram bot started")

    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        await _ptb_app.updater.stop()
        await _ptb_app.stop()
        await _ptb_app.shutdown()
        logger.info("Telegram bot stopped")
