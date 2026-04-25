from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db

from modal_backend.schemas.models import GroupGet, GroupPost
from modal_backend.settings import Settings, get_settings
from modal_backend.utils.services import GroupService


settings: Settings = get_settings()
group = APIRouter(prefix="/group", tags=["Group"])


@group.post("", response_model=GroupGet)
async def post_group(group: GroupPost, user=Depends(UnionAuth())) -> GroupGet:
    """ "
    Создает группу
    """
    new_group = await GroupService.create_service(db, group)
    return new_group
