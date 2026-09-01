from datetime import datetime, timezone

from requests import Session

from modal_backend.exceptions import ForbiddenAction, ObjectNotFound
from modal_backend.models.db import ModalStatus, Note, NoteView, Service, UserVisit


class UserService:
    """
    Пользовательский сервис для учёта показов модалок
    """

    @classmethod
    async def mark_view(cls, db: Session, note_id: int, user_id: int, service_id: int):
        note = Note.get(session=db.session, id=note_id)
        if note.status != ModalStatus.ACTIVE:
            raise ForbiddenAction(Note)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if note.is_always == False and now >= note.end_ts:
            raise ForbiddenAction(Note)

        service = Service.query(session=db.session).filter(Service.service_id == service_id).one_or_none()
        if service is None:
            raise ObjectNotFound(Service, service_id)

        user_visit = (
            UserVisit.query(session=db.session)
            .filter(UserVisit.user_id == user_id, UserVisit.service_id == service_id)
            .one_or_none()
        )
        visit_count = user_visit.visit_count if user_visit else 0

        note_view = (
            NoteView.query(session=db.session)
            .filter(NoteView.note_id == note_id, NoteView.user_id == user_id)
            .one_or_none()
        )
        if note_view is None:
            NoteView.create(
                session=db.session,
                note_id=note_id,
                user_id=user_id,
                shown_count=1,
                last_visit_number=1,
                first_shown_at=now,
                last_shown_at=now,
            )
        else:
            NoteView.update(
                note_view.id,
                session=db.session,
                shown_count=note_view.shown_count + 1,
                last_visit_number=visit_count,
                last_shown_at=now,
            )
