"""
Telegram bot service.
Handles /start <token> to link a user's Telegram account via a one-time token.
Started as a background task in main.py lifespan.
"""
import asyncio
import logging
import secrets
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

_ptb_app = None

# {token: (user_id, expires_at)}
_link_tokens: dict[str, tuple[int, datetime]] = {}
_TOKEN_TTL = timedelta(minutes=10)


def generate_link_token(user_id: int) -> str:
    """Generate a one-time token for linking Telegram account."""
    # Invalidate old tokens for this user
    for token, (uid, _) in list(_link_tokens.items()):
        if uid == user_id:
            del _link_tokens[token]
    token = secrets.token_urlsafe(16)
    _link_tokens[token] = (user_id, datetime.utcnow() + _TOKEN_TTL)
    return token


def _pop_token(token: str) -> int | None:
    """Consume token and return user_id, or None if invalid/expired."""
    entry = _link_tokens.pop(token, None)
    if not entry:
        return None
    user_id, expires_at = entry
    if datetime.utcnow() > expires_at:
        return None
    return user_id


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

        user_id = _pop_token(args[0])
        if not user_id:
            await update.message.reply_text("❌ Ссылка недействительна или устарела. Запросите новую в приложении.")
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
