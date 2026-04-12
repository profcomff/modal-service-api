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
    and_,
    case,
    exists,
    func,
    not_,
    select,
    text,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modal_backend.settings import Settings, get_settings

from .base import BaseDbModel

settings: Settings = get_settings()


class Class(BaseDbModel):
    pass
