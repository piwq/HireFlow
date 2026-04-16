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

# {chat_id: {"doc_type": str, "candidate_id": int, "expires_at": datetime}}
_pending_uploads: dict[str, dict] = {}
_UPLOAD_TTL = timedelta(minutes=15)


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


async def request_telegram_upload(chat_id: str, doc_type: str, candidate_id: int) -> bool:
    """Initiate a pending upload from Telegram."""
    if not _ptb_app:
        return False
    
    _pending_uploads[chat_id] = {
        "doc_type": doc_type,
        "candidate_id": candidate_id,
        "expires_at": datetime.utcnow() + _UPLOAD_TTL
    }
    
    try:
        await _ptb_app.bot.send_message(
            chat_id=chat_id,
            text=(
                f"📥 *Ожидаю файл* (тип: {doc_type})\n\n"
                "Пожалуйста, отправьте фото 📸 или документ 📄 прямо в этот чат.\n\n"
                "_Ссылка активна 15 минут._"
            ),
            parse_mode="Markdown"
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send upload request to TG: {e}")
        return False


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

    async def upload_handler(update: Update, context) -> None:
        chat_id = str(update.effective_chat.id)
        pending = _pending_uploads.get(chat_id)
        
        if not pending or datetime.utcnow() > pending["expires_at"]:
            if pending: del _pending_uploads[chat_id]
            return # Ignore if not expecting anything

        msg = update.message
        file_id = None
        filename = "telegram_upload"
        mime_type = "image/jpeg"
        MAX_SIZE = 10 * 1024 * 1024

        if msg.photo:
            photo = msg.photo[-1]
            if photo.file_size > MAX_SIZE:
                await msg.reply_text("❌ Фото слишком большое. Максимум 10 МБ.")
                return
            file_id = photo.file_id
            filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        elif msg.document:
            if msg.document.file_size > MAX_SIZE:
                await msg.reply_text("❌ Файл слишком большой. Максимум 10 МБ.")
                return
            
            allowed_mimes = [
                "application/pdf",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "image/jpeg",
                "image/png",
                "image/webp"
            ]
            if msg.document.mime_type not in allowed_mimes:
                await msg.reply_text("❌ Формат файла не поддерживается. Нужен PDF, Word или фото.")
                return

            file_id = msg.document.file_id
            filename = msg.document.file_name
            mime_type = msg.document.mime_type

        if not file_id:
            return

        await msg.reply_text("⏳ Обрабатываю файл...")

        try:
            tg_file = await context.bot.get_file(file_id)
            import io
            file_bytes = io.BytesIO()
            await tg_file.download_to_memory(file_bytes)
            file_bytes.seek(0)
            
            from app.services.s3 import upload_bytes
            url = await upload_bytes(file_bytes.read(), filename, msg.document.mime_type if msg.document else "image/jpeg")

            from app.models.document import Document
            async with AsyncSessionLocal() as db:
                doc = Document(
                    candidate_id=pending["candidate_id"],
                    doc_type=pending["doc_type"],
                    name=filename,
                    url=url
                )
                db.add(doc)
                await db.commit()
            
            del _pending_uploads[chat_id]
            await msg.reply_text(f"✅ Файл успешно загружен и добавлен в ваш профиль!\n\n📄 {filename}")
        except Exception as e:
            logger.error(f"Telegram upload failed: {e}")
            await msg.reply_text("❌ Произошла ошибка при загрузке. Попробуйте еще раз.")

    global _ptb_app
    _ptb_app = ApplicationBuilder().token(settings.telegram_bot_token).build()
    _ptb_app.add_handler(CommandHandler("start", start_handler))
    
    from telegram.ext import MessageHandler, filters
    _ptb_app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, upload_handler))

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
