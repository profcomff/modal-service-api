from __future__ import annotations

import datetime
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    true,
)
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import Mapped, mapped_column

from modal_backend.settings import Settings, get_settings

from .base import BaseDbModel


settings: Settings = get_settings()


class ModalStatus(str, Enum):
    ACTIVE: str = "active"
    ARCHIVED: str = "archived"


class NoteType(BaseDbModel):
    __tablename__ = "note_type"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Group(BaseDbModel):
    __tablename__ = "group"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Service(BaseDbModel):
    __tablename__ = "service"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Note(BaseDbModel):
    __tablename__ = "note"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("note_type.type_id"))
    header: Mapped[str] = mapped_column(String, nullable=False)
    info_text: Mapped[str | None] = mapped_column(String, nullable=True)  # type_id=1
    rating_max: Mapped[int | None] = mapped_column(Integer, nullable=True)  # type_id=2
    text: Mapped[str | None] = mapped_column(String, nullable=True)  # type_id=3
    max_length: Mapped[int | None] = mapped_column(Integer, nullable=True)  # type_id=3
    choice_options: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)  # type_id=4
    is_multiple: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # type_id=4
    images: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)  # type_id=5
    group_ids: Mapped[list[int]] = mapped_column(JSON)
    service_ids: Mapped[list[int]] = mapped_column(JSON)
    frequency: Mapped[int] = mapped_column(Integer)
    start_ts: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    end_ts: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    updated_ts: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    is_always: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    admin_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[ModalStatus] = mapped_column(String, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    @hybrid_method
    def search_by_type_id(self, query: int) -> bool:
        if not self.query:
            return true()
        return Note.type_id == query


class NoteResponse(BaseDbModel):
    __tablename__ = "note_response"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey("note.id"))
    user_id: Mapped[int] = mapped_column(Integer)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # type_id=2
    text: Mapped[str | None] = mapped_column(String, nullable=True)  # type_id=3
    selected_choices: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)  # type_id=4
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
