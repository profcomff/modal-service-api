from datetime import datetime, timezone

from requests import Session

from modal_backend.exceptions import AlreadyExists, ForbiddenAction, ObjectNotFound
from modal_backend.models.db import Group, ModalStatus, Note, Service
from modal_backend.schemas.base import StatusResponseModel
from modal_backend.schemas.models import GroupPost, ServicePost


class NoteService:
    """
    Сервис для работы с логикой Notifications и базой данных
    """

    @classmethod
    async def get_notes_by_filters(
        cls,
        db: Session,
        limit: int,
        offset: int,
        asc_order: bool,
        type_id: int = None,
        groups_id: list[int] = None,
        services_id: list[int] = None,
        status: ModalStatus | None = None,
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

    @classmethod
    async def update_status(cls, db: Session, id: int) -> Note:
        note = Note.get(session=db.session, id=id)
        if note.status == ModalStatus.ACTIVE:
            updated_note = Note.update(id=id, session=db.session, status=ModalStatus.ARCHIVED)
            return updated_note
        else:
            group_ids = note.group_ids
            new_group_ids = []
            for group_id in group_ids:
                group = db.session.query(Group).filter(Group.id == group_id, Group.is_deleted == False).one_or_none()
                if group is not None:
                    new_group_ids.append(group.id)
            if new_group_ids == []:
                raise ForbiddenAction(Note)

            service_ids = note.service_ids
            new_service_ids = []
            for service_id in service_ids:
                service = (
                    db.session.query(Service)
                    .filter(Service.id == service_id, Service.is_deleted == False)
                    .one_or_none()
                )
                if service is not None:
                    new_service_ids.append(service.id)
            if new_service_ids == []:
                raise ForbiddenAction(Note)

            end_ts = note.end_ts
            time = datetime.now(timezone.utc).replace(tzinfo=None)
            if note.is_always == False and time >= end_ts:
                raise ForbiddenAction(Note)
            updated_note = Note.update(
                id=id,
                session=db.session,
                group_ids=new_group_ids,
                service_ids=new_service_ids,
                status=ModalStatus.ACTIVE,
            )
            return updated_note


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

    @classmethod
    async def delete_service(cls, db: Session, id: int):
        Service.get(session=db.session, id=id)
        Service.delete(session=db.session, id=id)
        return StatusResponseModel(
            status="Success", message="Service has been successfully deleted", ru="Сервис успешно удален"
        )

    @classmethod
    async def update_service(cls, db: Session, id: int, service_info: ServicePost):
        Service.get(session=db.session, id=id)
        updated_service = Service.update(id, session=db.session, **service_info.model_dump())
        return updated_service


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

    @classmethod
    async def delete_group(cls, db: Session, id: int):
        Group.get(session=db.session, id=id)
        Group.delete(session=db.session, id=id)
        return StatusResponseModel(
            status="Success", message="Group has been successfully deleted", ru="Группа успешно удалена"
        )

    @classmethod
    async def update_group(cls, db: Session, id: int, group_info: GroupPost):
        Group.get(session=db.session, id=id)
        updated_group = Group.update(id, session=db.session, **group_info.model_dump())
        return updated_group
