from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, update, func as sa_func
from jose import jwt, JWTError

from app.config import settings
from app.database import get_db, AsyncSessionLocal
from app.deps import get_current_user
from app.models.user import User
from app.models.message import Message
from app.schemas.message import MessageResponse

router = APIRouter(tags=["chat"])


class ConnectionManager:
    def __init__(self):
        self.active: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, ws: WebSocket):
        await ws.accept()
        self.active[user_id] = ws

    def disconnect(self, user_id: int):
        self.active.pop(user_id, None)

    async def send_to(self, user_id: int, data: dict):
        ws = self.active.get(user_id)
        if ws:
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect(user_id)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, token: str = Query(...)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        await ws.close(code=1008)
        return

    await manager.connect(user_id, ws)
    try:
        while True:
            data = await ws.receive_json()
            receiver_id = data.get("receiver_id")
            text = str(data.get("text", "")).strip()
            if not text or not receiver_id:
                continue

            async with AsyncSessionLocal() as db:
                msg = Message(sender_id=user_id, receiver_id=receiver_id, text=text, is_read=False)
                db.add(msg)
                await db.commit()
                await db.refresh(msg)

            msg_data = {
                "id": msg.id,
                "sender_id": user_id,
                "receiver_id": receiver_id,
                "text": text,
                "created_at": msg.created_at.isoformat(),
            }

            # Send to receiver using unified notifications (so it hits Telegram and toast notifications)
            from app.services.notifications import notify_user
            await notify_user(receiver_id, "new_message", msg_data)
            # Echo back raw message to sender
            await manager.send_to(user_id, msg_data)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception:
        manager.disconnect(user_id)


@router.get("/messages/unread-counts")
async def unread_counts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return unread message counts grouped by sender: {sender_id: count}"""
    result = await db.execute(
        select(Message.sender_id, sa_func.count(Message.id))
        .where(
            Message.receiver_id == current_user.id,
            Message.is_read == False,
        )
        .group_by(Message.sender_id)
    )
    return {sender_id: count for sender_id, count in result.all()}


@router.get("/messages/{other_user_id}", response_model=list[MessageResponse])
async def get_conversation(
    other_user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Message)
        .where(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id),
            )
        )
        .order_by(Message.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    messages = list(result.scalars().all())
    messages.reverse()
    return messages


@router.post("/messages/read/{other_user_id}")
async def mark_read(
    other_user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all messages from other_user_id to current_user as read."""
    await db.execute(
        update(Message)
        .where(
            Message.sender_id == other_user_id,
            Message.receiver_id == current_user.id,
            Message.is_read == False,
        )
        .values(is_read=True)
    )
    await db.commit()
    return {"ok": True}

