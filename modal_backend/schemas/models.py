import datetime

from pydantic import model_validator

from modal_backend.exceptions import ValueError
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

    @model_validator(mode="after")
    def validate_by_type(self):
        if self.type_id == 1:
            if not self.info_text or not self.info_text.strip():
                raise ValueError("Для type_id=1 обязательно заполнить поле info_text")
        elif self.type_id == 2:
            if self.rating_max is None or self.rating_max < 1:
                raise ValueError("Для type_id=2 обязательно указать rating_max >= 1")
        elif self.type_id == 3:
            if not self.text or not self.text.strip():
                raise ValueError("Для type_id=3 обязательно заполнить поле text")
            if self.max_length is None or self.max_length < 1:
                raise ValueError("Для type_id=3 обязательно указать max_length > 0")
        elif self.type_id == 4:
            if not self.choice_options or len(self.choice_options) < 2:
                raise ValueError("Для type_id=4 обязательно указать минимум 2 варианта в choice_options")
            if self.is_multiple is None:
                self.is_multiple = False
        elif self.type_id == 5:
            if not self.images or len(self.images) == 0:
                raise ValueError("Для type_id=5 обязательно указать хотя бы одно изображение в images")
        else:
            raise ValueError(f"Недопустимый type_id: {self.type_id}. Разрешены только значения от 1 до 5")

        return self
