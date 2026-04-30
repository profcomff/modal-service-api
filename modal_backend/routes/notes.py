from typing import Union

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, Query
from fastapi_sqlalchemy import db

from modal_backend import settings
from modal_backend.models.db import ModalStatus, Note
from modal_backend.schemas.models import (
    NoteChoiceGet,
    NoteChoicePost,
    NoteGet,
    NoteImageGet,
    NoteImagePost,
    NoteInfoGet,
    NoteInfoPost,
    NoteRatingGet,
    NoteRatingPost,
    NoteTextGet,
    NoteTextPost,
    NotificationGet,
)
from modal_backend.settings import Settings, get_settings
from modal_backend.utils.services import NoteService


settings: Settings = get_settings()
note = APIRouter(prefix="/notification", tags=["Note"])


@note.get("", response_model=list[NoteGet])
async def get_notes(
    limit: int = 10,
    offset: int = 0,
    type_id: int = Query(None),
    groups_id: list[int] = Query(None),
    services_id: list[int] = Query(None),
    status: str = Query(
        enum=["active", "archived"],
        default=None,
    ),
    asc_order: bool = False,
    user=Depends(UnionAuth()),
) -> list[NoteGet]:
    """
    Получить список модалок по type_id.

    В случае несуществующего type_id ошибка ObjectNotFound
    """

    notes = await NoteService.get_note_by_type_id(db, type_id, limit, offset, groups_id, services_id, status, asc_order)
    return [NoteGet.model_validate(note) for note in notes]


@note.get("/{id}", response_model=Union[NoteInfoGet, NoteRatingGet, NoteTextGet, NoteChoiceGet, NoteImageGet])
async def get_note(
    id: int, user=Depends(UnionAuth())
) -> Union[NoteInfoGet, NoteRatingGet, NoteTextGet, NoteChoiceGet, NoteImageGet]:
    """
    Получить полную информацию о модалке по id.

    В случае несуществующего id ошибка ObjectNotFound
    """
    note = Note.get(session=db.session, id=id)
    schema_type = {
        1: NoteInfoGet,
        2: NoteRatingGet,
        3: NoteTextGet,
        4: NoteChoiceGet,
        5: NoteImageGet,
    }
    schema_class = schema_type.get(note.type_id)
    return schema_class.model_validate(note)


@note.post("/info", response_model=NoteInfoGet)
async def create_note_info(
    note: NoteInfoPost, user=Depends(UnionAuth(scopes=["modal.note.create"]))
) -> NotificationGet:
    """
    Создает новую модалку.

    Права: `["modal.note.create"]`
    """
    NoteService.validate_note_by_type(note, db)
    new_note = Note.create(session=db.session, **note.model_dump(), admin_id=user.get("id"), status=ModalStatus.ACTIVE)
    return NoteInfoGet.model_validate(new_note)


@note.post("/rating", response_model=NoteRatingGet)
async def create_note_rating(
    note: NoteRatingPost, user=Depends(UnionAuth(scopes=["modal.note.create"]))
) -> NotificationGet:
    """
    Создает новую модалку.

    Права: `["modal.note.create"]`
    """
    NoteService.validate_note_by_type(note, db)
    new_note = Note.create(session=db.session, **note.model_dump(), admin_id=user.get("id"), status=ModalStatus.ACTIVE)
    return NoteRatingGet.model_validate(new_note)


@note.post("/text", response_model=NoteTextGet)
async def create_note_text(
    note: NoteTextPost, user=Depends(UnionAuth(scopes=["modal.note.create"]))
) -> NotificationGet:
    """
    Создает новую модалку.

    Права: `["modal.note.create"]`
    """
    NoteService.validate_note_by_type(note, db)
    new_note = Note.create(session=db.session, **note.model_dump(), admin_id=user.get("id"), status=ModalStatus.ACTIVE)
    return NoteTextGet.model_validate(new_note)


@note.post("/choice", response_model=NoteChoiceGet)
async def create_note_choice(
    note: NoteChoicePost, user=Depends(UnionAuth(scopes=["modal.note.create"]))
) -> NotificationGet:
    """
    Создает новую модалку.

    Права: `["modal.note.create"]`
    """
    NoteService.validate_note_by_type(note, db)
    new_note = Note.create(session=db.session, **note.model_dump(), admin_id=user.get("id"), status=ModalStatus.ACTIVE)
    return NoteChoiceGet.model_validate(new_note)


@note.post("/image", response_model=NoteImageGet)
async def create_note_images(
    note: NoteImagePost, user=Depends(UnionAuth(scopes=["modal.note.create"]))
) -> NotificationGet:
    """
    Создает новую модалку.

    Права: `["modal.note.create"]`
    """
    NoteService.validate_note_by_type(note, db)
    new_note = Note.create(session=db.session, **note.model_dump(), admin_id=user.get("id"), status=ModalStatus.ACTIVE)
    return NoteImageGet.model_validate(new_note)
