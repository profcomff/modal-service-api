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


class ServiceGet(Base):
    id: int
    name: str


class ServicePost(Base):
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


class NoteInfoGet(NotificationGet):  # type_id=1
    info_text: str | None = None


class NoteRatingGet(NotificationGet):  # type_id=2
    rating_max: int | None = None


class NoteTextGet(NotificationGet):  # type_id=3
    text: str | None = None
    max_length: int | None = None


class NoteChoiceGet(NotificationGet):  # type_id=4
    choice_options: list[ChoiceOption] | None = None
    is_multiple: bool | None = None


class NoteImageGet(NotificationGet):  # type_id=5
    images: list[str] | None = None


class NotificationPost(Base):
    type_id: int
    header: str
    group_ids: list[int] | None = None
    service_ids: list[int] | None = None
    frequency: int
    start_ts: datetime.datetime | None = None
    end_ts: datetime.datetime | None = None
    is_always: bool


class NoteInfoPost(NotificationPost):  # type_id=1
    info_text: str | None = None


class NoteRatingPost(NotificationPost):  # type_id=2
    rating_max: int | None = None


class NoteTextPost(NotificationPost):  # type_id=3
    text: str | None = None
    max_length: int | None = None


class NoteChoicePost(NotificationPost):  # type_id=4
    choice_options: list[ChoiceOption] | None = None
    is_multiple: bool | None = None


class NoteImagePost(NotificationPost):  # type_id=5
    images: list[str] | None = None
