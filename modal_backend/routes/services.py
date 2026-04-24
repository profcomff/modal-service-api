from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db

from modal_backend import settings
from modal_backend.models.db import Service
from modal_backend.schemas.models import ServiceGet, ServicePost
from modal_backend.settings import Settings, get_settings
from modal_backend.utils.services import ServiceService


settings: Settings = get_settings()
service = APIRouter(prefix="/service", tags=["Service"])


@service.get("", response_model=ServiceGet)
async def get_service(
    id: int,
    user=Depends(UnionAuth()),
) -> ServiceGet:
    """
    Получить сервис по id.
    В случае несуществующего id ошибка ObjectNotFound
    """
    service = await ServiceService.get_service_by_id(db, id)
    return ServiceGet.model_validate(service)


@service.post("", response_model=ServiceGet)
async def create_service(
    service_info: ServicePost,
    user=Depends(UnionAuth(scopes=["modal.service.create"], allow_none=False)),
) -> ServiceGet:
    """
    Создает новый сервис.

    Права: `["modal.service.create"]`
    """
    new_service = Service.create(session=db.session, **service_info.model_dump())
    return ServiceGet.model_validate(new_service)
