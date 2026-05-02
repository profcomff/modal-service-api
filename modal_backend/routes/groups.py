from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db

from modal_backend.models.db import Group
from modal_backend.schemas.models import GroupGet, GroupPost
from modal_backend.settings import Settings, get_settings
from modal_backend.utils.services import GroupService
from modal_backend.schemas.base import StatusResponseModel

settings: Settings = get_settings()
group = APIRouter(prefix="/group", tags=["Group"])


@group.post("", response_model=GroupGet)
async def create_group(group: GroupPost, user=Depends(UnionAuth(["modal.group.create"]))) -> GroupGet:
    """
    Создает новую группу

    Scopes: `["modal.group.create"]`

    Исключение **AlreadyExists**, если группа с введеным `group_id` уже существует
    """
    new_group = await GroupService.create_group(db, **group.model_dump())
    return GroupGet.model_validate(new_group)


@group.get("", response_model=list[GroupGet])
async def get_groups(user=Depends(UnionAuth())) -> list[GroupGet]:
    """
    Получает список всех групп
    """
    groups = Group.query(session=db.session).all()
    return [GroupGet.model_validate(group) for group in groups]

@group.delete("/{id}", response_model=StatusResponseModel)
async def delete_group(id: int, user=Depends(UnionAuth(scopes=["modal.group.delete"]))):
    """
    Удаляет группу из базы данных

    Scopes: `["modal.group.delete"]`

    Исключение **ObjectNotFound**, если `id` не найден
    """
    del_group = await GroupService.delete_group(db, id)
    return del_group
