from typing import Union

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, Query
from fastapi_sqlalchemy import db

from modal_backend import settings
from modal_backend.models.db import ModalStatus, Note, NoteTypeEnum
from modal_backend.schemas.base import StatusResponseModel
from modal_backend.schemas.models import (
    NoteChoiceGet,
    NoteChoicePatch,
    NoteChoicePost,
    NoteGet,
    NoteImageGet,
    NoteImagePatch,
    NoteImagePost,
    NoteInfoGet,
    NoteInfoPatch,
    NoteInfoPost,
    NoteRatingGet,
    NoteRatingPatch,
    NoteRatingPost,
    NoteStatus,
    NoteTextGet,
    NoteTextPatch,
    NoteTextPost,
    NotificationGet,
)
from modal_backend.settings import Settings, get_settings
from modal_backend.utils.services import NoteService

settings: Settings = get_settings()
note = APIRouter(prefix="/notification", tags=["Note"])


@note.get("", response_model=list[NoteGet])
async def get_notes(
    type_id: int = Query(None),
    groups_id: list[int] = Query(None),
    services_id: list[int] = Query(None),
    status: ModalStatus = Query(
        enum=["active", "archived"],
        default=None,
    ),
    asc_order: bool = False,
    limit: int = Query(10, ge=0, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение записей на N+offset, где N - первая запись"),
    user=Depends(UnionAuth()),
) -> list[NoteGet]:
    """
    Получить список модалок по фильтрам

    `limit` - максимальное количество возвращаемых модалок

    `offset` -  смещение, определяющее, с какой по порядку модалки начинать выборку.
    Если без смещения возвращается модалка с условным номером N,
    то при значении offset = X будет возвращаться модалка с номером N + X

    `status` - возможные значения `"active", "archived"`.
    Если передано `'active'` - возвращается список активных модалок
    Если передано `'archived'` - возвращается список архивированных модалок

    `type_id` - вернет все модалки конкретного типа по type_id

    `groups_id` - вернет все модалки с конкретным groups_id

    `services_id` - вернет все модалки сервиса по id

    `asc_order` -Если передано true, сортировать в порядке возрастания. Иначе - в порядке убывания

    В случае несуществующего type_id ошибка ObjectNotFound
    """

    notes = await NoteService.get_notes_by_filters(
        db, limit, offset, asc_order, type_id, groups_id, services_id, status
    )
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
        NoteTypeEnum.INFO: NoteInfoGet,
        NoteTypeEnum.RATING: NoteRatingGet,
        NoteTypeEnum.TEXT: NoteTextGet,
        NoteTypeEnum.CHOICE: NoteChoiceGet,
        NoteTypeEnum.IMAGE: NoteImageGet,
    }
    schema_class = schema_type.get(note.type_id)
    return schema_class.model_validate(note)


@note.post("/info", response_model=NoteInfoGet)
async def create_note_info(
    note: NoteInfoPost, user=Depends(UnionAuth(scopes=["modal.note.create"]))
) -> NotificationGet:
    """
    Создает новую модалку.

    Тип - простое информационное сообщение / новость

    Поле для записи: info_text

    Права: `["modal.note.create"]`
    """
    new_note = Note.create(
        session=db.session,
        type_id=NoteTypeEnum.INFO,
        **note.model_dump(),
        admin_id=user.get("id"),
        status=ModalStatus.ACTIVE,
    )
    return NoteInfoGet.model_validate(new_note)


@note.post("/rating", response_model=NoteRatingGet)
async def create_note_rating(
    note: NoteRatingPost, user=Depends(UnionAuth(scopes=["modal.note.create"]))
) -> NotificationGet:
    """
    Создает новую модалку.

    Тип модалки - оценка (рейтинг от 1 до 5)

    Поле для записи: rating_max

    Права: `["modal.note.create"]`
    """
    new_note = Note.create(
        session=db.session,
        type_id=NoteTypeEnum.RATING,
        **note.model_dump(),
        admin_id=user.get("id"),
        status=ModalStatus.ACTIVE,
    )
    return NoteRatingGet.model_validate(new_note)


@note.post("/text", response_model=NoteTextGet)
async def create_note_text(
    note: NoteTextPost, user=Depends(UnionAuth(scopes=["modal.note.create"]))
) -> NotificationGet:
    """
    Создает новую модалку.

    Тип модалки - ввод произвольного текста

    Поля для записи: text и max_length (максимальная длина произвольного текста)

    Права: `["modal.note.create"]`
    """
    new_note = Note.create(
        session=db.session,
        type_id=NoteTypeEnum.TEXT,
        **note.model_dump(),
        admin_id=user.get("id"),
        status=ModalStatus.ACTIVE,
    )
    return NoteTextGet.model_validate(new_note)


@note.post("/choice", response_model=NoteChoiceGet)
async def create_note_choice(
    note: NoteChoicePost, user=Depends(UnionAuth(scopes=["modal.note.create"]))
) -> NotificationGet:
    """
    Создает новую модалку.

    Тип модалки - выбор одного или нескольких вариантов ответа

    Поля для записи: choice_options (пример [{"id": 1, "text": "текст"}, ...]) и is_multiple (bool, множественный ли выбор)

    Права: `["modal.note.create"]`
    """
    new_note = Note.create(
        session=db.session,
        type_id=NoteTypeEnum.CHOICE,
        **note.model_dump(),
        admin_id=user.get("id"),
        status=ModalStatus.ACTIVE,
    )
    return NoteChoiceGet.model_validate(new_note)


@note.post("/image", response_model=NoteImageGet)
async def create_note_images(
    note: NoteImagePost, user=Depends(UnionAuth(scopes=["modal.note.create"]))
) -> NotificationGet:
    """
    Создает новую модалку.

    Тип модалки - сторис

    Поле для записи: images (пример ["url1","url2"])

    Права: `["modal.note.create"]`
    """
    new_note = Note.create(
        session=db.session,
        type_id=NoteTypeEnum.IMAGE,
        **note.model_dump(),
        admin_id=user.get("id"),
        status=ModalStatus.ACTIVE,
    )
    return NoteImageGet.model_validate(new_note)


@note.patch("/info/{id}", response_model=NoteInfoGet)
async def update_note_info(
    id: int, note_info: NoteInfoPatch, user=Depends(UnionAuth(scopes=["modal.note.patch"]))
) -> NoteInfoGet:
    updated_note = await NoteService.update_note(db, id, note_info, NoteTypeEnum.INFO)
    return NoteInfoGet.model_validate(updated_note)


@note.patch("/rating/{id}", response_model=NoteRatingGet)
async def update_note_rating(
    id: int, note_info: NoteRatingPatch, user=Depends(UnionAuth(scopes=["modal.note.patch"]))
) -> NoteRatingGet:
    updated_note = await NoteService.update_note(db, id, note_info, NoteTypeEnum.RATING)
    return NoteRatingGet.model_validate(updated_note)


@note.patch("/text/{id}", response_model=NoteTextGet)
async def update_note_text(
    id: int, note_info: NoteTextPatch, user=Depends(UnionAuth(scopes=["modal.note.patch"]))
) -> NoteTextGet:
    updated_note = await NoteService.update_note(db, id, note_info, NoteTypeEnum.TEXT)
    return NoteTextGet.model_validate(updated_note)


@note.patch("/choice/{id}", response_model=NoteChoiceGet)
async def update_note_choice(
    id: int, note_info: NoteChoicePatch, user=Depends(UnionAuth(scopes=["modal.note.patch"]))
) -> NoteChoiceGet:
    updated_note = await NoteService.update_note(db, id, note_info, NoteTypeEnum.CHOICE)
    return NoteChoiceGet.model_validate(updated_note)


@note.patch("/image/{id}", response_model=NoteImageGet)
async def update_note_image(
    id: int, note_info: NoteImagePatch, user=Depends(UnionAuth(scopes=["modal.note.patch"]))
) -> NoteImageGet:
    updated_note = await NoteService.update_note(db, id, note_info, NoteTypeEnum.IMAGE)
    return NoteImageGet.model_validate(updated_note)


@note.patch("/{id}/status", response_model=NoteStatus)
async def update_note_status(id: int, user=Depends(UnionAuth(scopes=["modal.note.patch"]))) -> NoteStatus:
    """
    Архивирует модалку, если она активна

    Если модалка в архиве, возвращает её в активное состояние, убирая из `group_ids` и `service_ids` ненайденные группы и сервисы

    Права: `["modal.note.patch"]`

    Исключение **ObjectNotFound**, если `id` не найден

    Исключения, которые могут возникнуть при возврате в активное состояние:

    Исключение **ForbiddenAction**, если ни одна группа из списка `group_ids` не найдена

    Исключение **ForbiddenAction**, если ни один сервис из списка `service_ids` не найден

    Исключение **ForbiddenAction**, если время модалки истекло
    """
    updated_note = await NoteService.update_status(db, id=id)
    return NoteStatus.model_validate(updated_note)


@note.delete("/{id}", response_model=StatusResponseModel)
async def delete_note(id: int, user=Depends(UnionAuth(scopes=["modal.note.delete"]))) -> StatusResponseModel:
    """
    Удаляет модалку по id

    Права: `["modal.note.delete"]`

    Исключение **ObjectNotFound**, если `id` не найден
    """
    Note.get(session=db.session, id=id)
    Note.delete(session=db.session, id=id)
    return StatusResponseModel(
        status="success", message="Note has been successfully deleted", ru="Модалка успешно удалена"
    )
