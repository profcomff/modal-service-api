from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db

from modal_backend import settings
from modal_backend.models.db import NoteType
from modal_backend.schemas.models import NoteTypeGet, NoteTypePost
from modal_backend.settings import Settings, get_settings
from modal_backend.utils.services import NoteTypeService


settings: Settings = get_settings()
notetype = APIRouter(prefix="/notificationtype", tags=["NoteType"])


@notetype.get("", response_model=list[NoteTypeGet])
async def get_notes(user=Depends(UnionAuth())) -> list[NoteTypeGet]:
    """
    Получить список типов модалок.
    """
    note_types = NoteType.query(session=db.session).all()
    return [NoteTypeGet.model_validate(note) for note in note_types]


@notetype.post("", response_model=NoteTypeGet)
async def create_note_type(
    note_type: NoteTypePost, user=Depends(UnionAuth(scopes=["modal.note_type.create"]))
) -> NoteTypeGet:
    """
    Создает новый тип модалок.

    Права: `["modal.note_type.create"]`
    """
    new_note_type = await NoteTypeService.create_note_type(db, note_type=note_type)
    return NoteTypeGet.model_validate(new_note_type)
