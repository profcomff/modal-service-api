import datetime

from modal_backend.models.db import ModalStatus
from modal_backend.schemas.base import Base


class NoteGet(Base):
    id: int
    type_id: int
    header: str
    end_ts: datetime
    status: ModalStatus
    is_available: bool = False
