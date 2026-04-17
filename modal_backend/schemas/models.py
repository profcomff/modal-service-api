import datetime

from modal_backend.models.db import ModalStatus
from modal_backend.schemas.base import Base


class NoteGet(Base):
    id: int
    type_id: int
    header: str
    end_ts: datetime.datetime
    status: ModalStatus


class ChoiceOption(Base):
    id: int
    text: str


class NoteTypePost(Base):
    type_id: int
    name: str


class NoteTypeGet(Base):
    id: int
    type_id: int
    name: str


class NotificationGet(Base):
    id: int
    type_id: int
    header: str
    group_ids: list[int] | None = None
    service_ids: list[int] | None = None
    frequency: int
    start_ts: datetime.datetime | None = None
    end_ts: datetime.datetime | None = None
    updated_ts: datetime.datetime | None = None
    is_always: bool
    admin_id: int
    status: ModalStatus
    view_count: int
    rejected_count: int
    info_text: str | None = None  # type_id=1
    rating_max: int | None = None  # type_id=2
    text: str | None = None  # type_id=3
    max_length: int | None = None  # type_id=3
    choice_options: list[ChoiceOption] | None = None  # type_id=4
    is_multiple: bool | None = None  # type_id=4
    images: list[str] | None = None  # type_id=5


class NotificationPost(Base):
    type_id: int
    header: str
    group_ids: list[int] | None = None
    service_ids: list[int] | None = None
    frequency: int
    start_ts: datetime.datetime | None = None
    end_ts: datetime.datetime | None = None
    is_always: bool
    info_text: str | None = None  # type_id=1
    rating_max: int | None = None  # type_id=2
    text: str | None = None  # type_id=3
    max_length: int | None = None  # type_id=3
    choice_options: list[ChoiceOption] | None = None  # type_id=4
    is_multiple: bool | None = None  # type_id=4
    images: list[str] | None = None  # type_id=5
