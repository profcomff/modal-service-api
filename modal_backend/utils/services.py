from requests import Session

from modal_backend.models.db import Note, NoteType
from modal_backend.settings import Settings


class NoteService:
    """
    Сервис для работы с логикой Notifications и базой данных
    """

    settings = Settings()

    @classmethod
    async def get_note_by_type_id(cls, db: Session, type_id: int):
        query = Note.query(session=db.session)
        NoteType.get(type_id, session=db.session)
        query = query.filter(Note.type_id == type_id)
        notes = query.all()
        return notes
