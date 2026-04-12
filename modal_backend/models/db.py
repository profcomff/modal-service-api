from __future__ import annotations

from modal_backend.settings import Settings, get_settings

from .base import BaseDbModel


settings: Settings = get_settings()


class Class(BaseDbModel):
    pass
