"""
Notification service.
Sends real-time events via WebSocket + Telegram (if user linked their account).
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone, timedelta
from app.routers.chat import manager
from app.models.message import Message
from sqlalchemy import select, func

logger = logging.getLogger(__name__)

# {user_id: {"message_id": int, "chat_id": str, "timestamp": datetime}}
_tg_message_registry = {}
_BUNDLE_WINDOW = timedelta(minutes=5)

_STATUS_LABELS = {
    "new": "Новый", "screening": "На рассмотрении", "interview": "HR-интервью",
    "manager_interview": "Интервью с руководителем", "interview_done": "Интервью проведено",
    "awaiting_decision": "Ожидает решения", "reserve": "Резерв", "offer": "Получен оффер",
    "hired": "Принят на работу", "rejected": "Отказ", "accepted": "Принят",
}


def _tg_text(event: str, data: dict, bundle_info: dict | None = None) -> str:
    if event == "application_status":
        label = _STATUS_LABELS.get(data.get("status", ""), data.get("status", ""))
        return f"📋 HireFlow\nСтатус заявки изменён: {label}"
    if event in ("interview_scheduled", "interview_assigned", "interview_rescheduled"):
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(data["scheduled_at"]).strftime("%d.%m.%Y %H:%M")
        except Exception:
            dt = data.get("scheduled_at", "")
            
        link = ""
        room_code = data.get("room_code")
        if room_code:
            from app.config import settings
            link = f"\n🔗 Вход на интервью: {settings.frontend_url}/call/{room_code}"
            
        if event == "interview_rescheduled":
            return f"📅 HireFlow\nВремя интервью изменено на {dt}{link}"
            
        return f"📅 HireFlow\nВам назначено интервью на {dt}{link}"
    if event == "interview_request_new":
        return "🔔 HireFlow\nНовый запрос на интервью от руководителя"
    if event == "interview_request_updated":
        if data.get("status") == "accepted":
            return "✅ HireFlow\nВаш запрос на интервью принят"
        return "❌ HireFlow\nВаш запрос на интервью отклонён"
    if event == "new_message":
        if bundle_info:
            total = bundle_info["total"]
            chats = bundle_info["chats"]
            # Russian pluralization rules for "сообщение" and "чат" are complex, 
            # using simple "сообщений" and "чатов" for brevity as requested.
            return f"💬 HireFlow\nУ вас {total} непрочитанных сообщений из {chats} чатов"
        return "💬 HireFlow\nУ вас новое сообщение в чате"
    return "💬 HireFlow\nНовое уведомление"


async def _send_telegram(chat_id: str, text: str) -> int | None:
    from app.config import settings
    if not settings.telegram_bot_token:
        return None
    try:
        from telegram import Bot
        async with Bot(token=settings.telegram_bot_token) as bot:
            msg = await bot.send_message(chat_id=chat_id, text=text)
            return msg.message_id
    except Exception as e:
        logger.warning("Telegram send failed: %s", e)
        return None


async def _edit_telegram(chat_id: str, message_id: int, text: str) -> bool:
    from app.config import settings
    if not settings.telegram_bot_token:
        return False
    try:
        from telegram import Bot
        async with Bot(token=settings.telegram_bot_token) as bot:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)
            return True
    except Exception as e:
        logger.warning("Telegram edit failed: %s", e)
        return False


async def notify_user(user_id: int, event: str, data: dict) -> None:
    # WebSocket (in-app)
    await manager.send_to(user_id, {"type": "notification", "event": event, "data": data})

    # Telegram
    try:
        from app.database import AsyncSessionLocal
        from app.models.user import User
        async with AsyncSessionLocal() as db:
            res = await db.execute(
                select(User.telegram_chat_id).where(User.id == user_id)
            )
            row = res.first()
            if not (row and row[0]):
                return
                
            tg_chat_id = row[0]
            
            if event == "new_message":
                # Get current unread counts
                counts_res = await db.execute(
                    select(Message.sender_id, func.count(Message.id))
                    .where(Message.receiver_id == user_id, Message.is_read == False)
                    .group_by(Message.sender_id)
                )
                unread_data = counts_res.all()
                total_unread = sum(r[1] for r in unread_data)
                unique_chats = len(unread_data)
                
                if total_unread == 0:
                    return # Should not happen if new_message was just sent
                
                bundle_info = {"total": total_unread, "chats": unique_chats}
                now = datetime.now(timezone.utc)
                
                reg = _tg_message_registry.get(user_id)
                if reg and (now - reg["timestamp"]) < _BUNDLE_WINDOW:
                    # Update existing message
                    success = await _edit_telegram(tg_chat_id, reg["message_id"], _tg_text(event, data, bundle_info))
                    if success:
                        reg["timestamp"] = now # Sliding window
                        return
                
                # Send new message if no recent one or edit failed
                msg_id = await _send_telegram(tg_chat_id, _tg_text(event, data, bundle_info))
                if msg_id:
                    _tg_message_registry[user_id] = {"message_id": msg_id, "timestamp": now}
            else:
                # Normal notification
                await _send_telegram(tg_chat_id, _tg_text(event, data))
                
    except Exception as e:
        logger.warning("notify_user telegram lookup failed: %s", e)


async def notify_users(user_ids: list[int], event: str, data: dict) -> None:
    for uid in user_ids:
        await notify_user(uid, event, data)
