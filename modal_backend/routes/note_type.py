from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db

from modal_backend import settings
from modal_backend.schemas.models import NoteTypeGet, NoteTypePost
from modal_backend.settings import Settings, get_settings
from modal_backend.utils.services import NoteTypeService


settings: Settings = get_settings()
notetype = APIRouter(prefix="/notificationtype", tags=["NoteType"])


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
