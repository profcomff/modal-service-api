from alembic.environment import List, Optional
from requests import Session

from modal_backend.exceptions import AlreadyExists, ObjectNotFound
from modal_backend.models.db import Group, ModalStatus, Note, NoteType, Service
from modal_backend.schemas.models import NoteTypePost, NotificationPost


class NoteService:
    """
    Сервис для работы с логикой Notifications и базой данных
    """

    @classmethod
    async def get_notes_by_filters(
        cls,
        db: Session,
        type_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
        groups_id: Optional[List[int]] = None,
        services_id: Optional[List[int]] = None,
        status: Optional[str] = None,
        asc_order: Optional[bool] = True,
    ):
        notes_query = (
            Note.query(session=db.session)
            .filter(Note.search_by_type_id(type_id))
            .filter(Note.search_by_group_ids(groups_id))
            .filter(Note.search_by_service_ids(services_id))
            .filter(Note.search_by_status(status))
        )

        order_expr = Note.start_ts.asc() if asc_order else Note.start_ts.desc()
        notes_query = notes_query.order_by(order_expr)

        notes = notes_query.limit(limit).offset(offset).all()

        if not notes:
            raise ObjectNotFound(Note, 'all')

        return notes

    @staticmethod
    def validate_note_by_type(note: dict, db: Session):
        type_id = note.type_id
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


class ServiceManager:
    """
    Сервис для работы с логикой Service и базой данных
    """

    @classmethod
    async def create_service(cls, db: Session, service_id: int, name: str):
        service = Service.query(session=db.session).filter(Service.service_id == service_id).first()
        if service:
            raise AlreadyExists(Service, service_id)
        new_service = Service.create(session=db.session, service_id=service_id, name=name)
        return new_service


class GroupService:
    """
    Сервис для работы с логикой Group и базой данных
    """

    @classmethod
    async def create_group(cls, db: Session, group_id: int, name: str):
        group = Group.query(session=db.session).filter(Group.group_id == group_id).first()
        if group:
            raise AlreadyExists(Group, group_id)
        new_group = Group.create(session=db.session, group_id=group_id, name=name)
        return new_group
