from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import require_role
from app.models.user import User
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/", response_model=NoteResponse, status_code=201)
async def create_note(
    body: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("hr", "admin")),
):
    note = Note(
        candidate_id=body.candidate_id,
        author_id=current_user.id,
        text=body.text,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.get("/candidate/{candidate_id}", response_model=list[NoteResponse])
async def list_notes(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "admin")),
):
    result = await db.execute(
        select(Note)
        .where(Note.candidate_id == candidate_id)
        .order_by(Note.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/{note_id}", status_code=204)
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("hr", "admin")),
):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your note")
    await db.delete(note)
    await db.commit()
