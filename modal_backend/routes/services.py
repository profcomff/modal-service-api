from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db

from modal_backend.models.db import Service
from modal_backend.schemas.base import StatusResponseModel
from modal_backend.schemas.models import ServiceGet, ServicePost
from modal_backend.settings import Settings, get_settings
from modal_backend.utils.services import ServiceManager


settings: Settings = get_settings()
service = APIRouter(prefix="/service", tags=["Service"])


@service.get("", response_model=list[ServiceGet])
async def get_services(
    user=Depends(UnionAuth()),
) -> list[ServiceGet]:
    """
    Получить список всех сервисов.
    """
    services = Service.query(session=db.session).all()
    return [ServiceGet.model_validate(service) for service in services]


@service.post("", response_model=ServiceGet)
async def create_service(
    service_info: ServicePost,
    user=Depends(UnionAuth(scopes=["modal.service.create"])),
) -> ServiceGet:
    """
    Создает новый сервис.

    Права: `["modal.service.create"]`
    """
    new_service = await ServiceManager.create_service(db, **service_info.model_dump())
    return ServiceGet.model_validate(new_service)


@service.delete("/{id}", response_model=StatusResponseModel)
async def delete_service(id: int, user=Depends(UnionAuth(scopes=["modal.service.delete"]))) -> StatusResponseModel:
    """
    Удаляет сервис из базы данных

    Scopes: `["modal.service.delete"]`

    Исключение **ObjectNotFound**, если `id` не найден
    """
    return await ServiceManager.delete_service(db, id)
