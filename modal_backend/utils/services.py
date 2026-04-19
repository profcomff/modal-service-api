from requests import Session

from modal_backend.exceptions import AlreadyExists, ObjectNotFound
from modal_backend.models.db import ModalStatus, Note, NoteType
from modal_backend.schemas.models import NoteTypePost, NotificationPost


class NoteService:
    """
    Сервис для работы с логикой Notifications и базой данных
    """

    @classmethod
    async def get_note_by_type_id(cls, db: Session, type_id: int):
        note_type = NoteType.query(session=db.session).filter(NoteType.type_id == type_id).one_or_none()
        if note_type is None:
            raise ObjectNotFound(NoteType, type_id)
        notes = Note.query(session=db.session).filter(Note.type_id == type_id).all()
        return notes

    @staticmethod
    def validate_note_by_type(note: dict, db: Session):
        type_id = note.get("type_id")
        note_type = NoteType.query(session=db.session).filter(NoteType.type_id == type_id).one_or_none()
        if note_type is None:
            raise ObjectNotFound(NoteType, type_id)

    @classmethod
    async def create_note(cls, db: Session, note: NotificationPost, admin_id: int) -> Note:
        cls.validate_note_by_type(note, db)
        new_note = Note.create(session=db.session, **note, admin_id=admin_id, status=ModalStatus.ACTIVE)
        return new_note


class NoteTypeService:
    """
    Сервис для работы с логикой NoteType и базой данных
    """

    @classmethod
    async def create_note_type(cls, db: Session, note_type: NoteTypePost) -> NoteType:
        data = note_type.model_dump()
        type_id = data.get("type_id")
        note_types = NoteType.query(session=db.session).filter(NoteType.type_id == type_id).first()
        if note_types:
            raise AlreadyExists(NoteType, type_id)
        new_note_type = NoteType.create(session=db.session, **data)
        return new_note_type
