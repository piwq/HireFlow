import time
from fastapi import APIRouter, Depends, Query
from jose import jwt

from app.config import settings
from app.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/livekit", tags=["livekit"])


def _make_token(room: str, identity: str, name: str) -> str:
    now = int(time.time())
    payload = {
        "exp": now + 3600,
        "iss": settings.livekit_api_key,
        "nbf": now - 5,
        "sub": identity,
        "video": {
            "room": room,
            "roomJoin": True,
            "canPublish": True,
            "canSubscribe": True,
            "canPublishData": True,
        },
        "name": name,
        "metadata": "",
    }
    return jwt.encode(payload, settings.livekit_api_secret, algorithm="HS256")


@router.get("/token")
async def get_token(
    room: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    token = _make_token(
        room=room,
        identity=str(current_user.id),
        name=current_user.email,
    )
    return {"token": token}
