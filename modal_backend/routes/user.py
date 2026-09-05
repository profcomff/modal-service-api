from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db

from modal_backend.schemas.base import StatusResponseModel
from modal_backend.settings import Settings, get_settings
from modal_backend.utils.user_logic import UserService

settings: Settings = get_settings()
user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.post("/{id}/view", response_model=StatusResponseModel)
async def mark_note_view(
    id: int,
    service_id: int,
    user=Depends(UnionAuth()),
) -> StatusResponseModel:
    """
    Отмечает, что модалка реально была показана пользователю.

    Увеличивает shown_count в таблице note_view и запоминает номер захода
    (last_visit_number), от которого потом считается frequency.
    Если записи в note_view ещё нет — создаёт.

    Повторный вызов не ошибка
    """
    await UserService.mark_view(db, note_id=id, user_id=user.get("id"), service_id=service_id)
    return StatusResponseModel(status="success", message="View recorded", ru="Показ засчитан")
