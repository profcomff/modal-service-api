from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, Query
from fastapi_sqlalchemy import db

from modal_backend import settings
from modal_backend.models.db import ModalStatus, Note
from modal_backend.schemas.models import NoteGet, NotificationGet, NotificationPost
from modal_backend.settings import Settings, get_settings


settings: Settings = get_settings()
note = APIRouter(prefix="/notification", tags=["Notes"])


@note.get("", response_model=list[NoteGet])
async def get_notes(type_id: int = Query(None), user=Depends(UnionAuth())) -> list[NoteGet]:
    """
    Получить модалку
    """
    query = Note.query(session=db.session)
    if type_id is not None:
        query = query.filter(Note.type_id == type_id)
    notes = query.all()
    return [NoteGet.model_validate(note) for note in notes]


@note.post("", response_model=NotificationGet)
async def create_note(note: NotificationPost, user=Depends(UnionAuth(scopes=["modal.note.create"]))) -> NotificationGet:
    """
    Создает новую модалку.

    Права: `["modal.note.create"]`
    """
    new_note = Note.create(session=db.session, **note.model_dump(), admin_id=user.get('id'), status=ModalStatus.ACTIVE)
    return NotificationGet.model_validate(new_note)
