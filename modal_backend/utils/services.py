from requests import Session

from modal_backend.exceptions import AlreadyExists, ValueError
from modal_backend.models.db import ModalStatus, Note, NoteType
from modal_backend.schemas.models import NoteTypePost, NotificationPost


class NoteService:
    """
    Сервис для работы с логикой Notifications и базой данных
    """

    @classmethod
    async def get_note_by_type_id(cls, db: Session, type_id: int):
        NoteType.get(type_id, session=db.session)
        notes = Note.query(session=db.session).filter(Note.type_id == type_id).all()
        return notes

    @staticmethod
    def validate_note_by_type(data: dict):
        type_id = data["type_id"]
        if type_id == 1:
            info_text = data.get("info_text")
            if not info_text or not info_text.strip():
                raise ValueError("Для type_id=1 обязательно заполнить поле info_text")
        elif type_id == 2:
            rating_max = data.get("rating_max")
            if rating_max is None or rating_max < 1:
                raise ValueError("Для type_id=2 обязательно указать rating_max >= 1")
        elif type_id == 3:
            text = data.get("text")
            max_length = data.get("max_length")
            if not text or not text.strip():
                raise ValueError("Для type_id=3 обязательно заполнить поле text")
            if max_length is None or max_length < 1:
                raise ValueError("Для type_id=3 обязательно указать max_length > 0")
        elif type_id == 4:
            choice_options = data.get("choice_options")
            is_multiple = data.get("is_multiple")
            if not choice_options or len(choice_options) < 2:
                raise ValueError("Для type_id=4 обязательно указать минимум 2 варианта в choice_options")
            if is_multiple is None:
                data["is_multiple"] = False
        elif type_id == 5:
            images = data.get("images")
            if not images or len(images) == 0:
                raise ValueError("Для type_id=5 обязательно указать хотя бы одно изображение в images")
        else:
            raise ValueError(f"Недопустимый type_id: {type_id}. Разрешены только значения от 1 до 5")

    @classmethod
    async def create_note(cls, db: Session, note: NotificationPost, admin_id: int) -> Note:
        data = note.model_dump()
        cls.validate_note_by_type(data)
        new_note = Note.create(session=db.session, **data, admin_id=admin_id, status=ModalStatus.ACTIVE)
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
