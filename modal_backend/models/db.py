from __future__ import annotations

import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from modal_backend.settings import Settings, get_settings

from .base import BaseDbModel


settings: Settings = get_settings()


class ModalStatus(str, Enum):
    ACTIVE: str = "active"
    ARCHIEVED: str = "archieved"


class NoteType(BaseDbModel):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Group(BaseDbModel):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Service(BaseDbModel):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Note(BaseDbModel):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("NoteType.id"))
    header: Mapped[str] = mapped_column(String, nullable=False)
    info_text: Mapped[str | None] = mapped_column(String, nullable=True)  # type_id=1
    rating_max: Mapped[int | None] = mapped_column(Integer, nullable=True)  # type_id=2
    text: Mapped[str | None] = mapped_column(String, nullable=True)  # type_id=3
    max_length: Mapped[int | None] = mapped_column(Integer, nullable=True)  # type_id=3
    choice_options: Mapped[list[dict] | None] = mapped_column(String, nullable=True)  # type_id=4
    is_multiple: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # type_id=4
    images: Mapped[list[str] | None] = mapped_column(String, nullable=True)  # type_id=5
    group_ids: Mapped[list[int]] = mapped_column(Integer)
    service_ids: Mapped[list[int]] = mapped_column(Integer)
    frequency: Mapped[int] = mapped_column(Integer)
    start_ts: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    env_ts: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    updated_ts: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    is_always: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    admin_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[ModalStatus] = mapped_column(String, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class NoteResponse(BaseDbModel):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey("Note.id"))
    user_id: Mapped[int] = mapped_column(Integer)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # type_id=2
    text: Mapped[str | None] = mapped_column(String, nullable=True)  # type_id=3
    selected_choices: Mapped[list[dict] | None] = mapped_column(String, nullable=True)  # type_id=4
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
