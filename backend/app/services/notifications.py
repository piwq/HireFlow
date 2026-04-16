"""
Notification service.
Sends real-time events via WebSocket + Telegram (if user linked their account).
"""
from __future__ import annotations
import logging
from app.routers.chat import manager

logger = logging.getLogger(__name__)

_STATUS_LABELS = {
    "new": "Новый", "screening": "На рассмотрении", "interview": "HR-интервью",
    "manager_interview": "Интервью с руководителем", "interview_done": "Интервью проведено",
    "awaiting_decision": "Ожидает решения", "reserve": "Резерв", "offer": "Получен оффер",
    "hired": "Принят на работу", "rejected": "Отказ", "accepted": "Принят",
}


def _tg_text(event: str, data: dict) -> str:
    if event == "application_status":
        label = _STATUS_LABELS.get(data.get("status", ""), data.get("status", ""))
        return f"📋 HireFlow\nСтатус заявки изменён: {label}"
    if event == "interview_scheduled":
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(data["scheduled_at"]).strftime("%d.%m.%Y %H:%M")
        except Exception:
            dt = data.get("scheduled_at", "")
        return f"📅 HireFlow\nВам назначено интервью на {dt}"
    if event == "interview_assigned":
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(data["scheduled_at"]).strftime("%d.%m.%Y %H:%M")
        except Exception:
            dt = data.get("scheduled_at", "")
        return f"📅 HireFlow\nВам назначено интервью на {dt}"
    if event == "interview_request_new":
        return "🔔 HireFlow\nНовый запрос на интервью от руководителя"
    if event == "interview_request_updated":
        if data.get("status") == "accepted":
            return "✅ HireFlow\nВаш запрос на интервью принят"
        return "❌ HireFlow\nВаш запрос на интервью отклонён"
    return "💬 HireFlow\nНовое уведомление"


async def _send_telegram(chat_id: str, text: str) -> None:
    from app.config import settings
    if not settings.telegram_bot_token:
        return
    try:
        from telegram import Bot
        async with Bot(token=settings.telegram_bot_token) as bot:
            await bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        logger.warning("Telegram send failed: %s", e)


async def notify_user(user_id: int, event: str, data: dict) -> None:
    # WebSocket (in-app)
    await manager.send_to(user_id, {"type": "notification", "event": event, "data": data})

    # Telegram
    try:
        from app.database import AsyncSessionLocal
        from app.models.user import User
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            res = await db.execute(
                select(User.telegram_chat_id).where(User.id == user_id)
            )
            row = res.first()
            if row and row[0]:
                await _send_telegram(row[0], _tg_text(event, data))
    except Exception as e:
        logger.warning("notify_user telegram lookup failed: %s", e)


async def notify_users(user_ids: list[int], event: str, data: dict) -> None:
    for uid in user_ids:
        await notify_user(uid, event, data)
