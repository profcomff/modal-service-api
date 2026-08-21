from starlette import status

from modal_backend.models.db import NoteView

url = "/user"


def test_first_view_creates_note_view(client, dbsession, notes, authlib_user_data):
    note = notes[0]

    response = client.post(f"{url}/{note.id}/view", params={"service_id": 1})
    assert response.status_code == status.HTTP_200_OK

    view = (
        dbsession.query(NoteView)
        .filter(NoteView.note_id == note.id, NoteView.user_id == authlib_user_data["id"])
        .one_or_none()
    )
    assert view is not None
    assert view.shown_count == 1

    dbsession.delete(view)
    dbsession.commit()


def test_second_view_increments_shown_count(client, dbsession, notes, authlib_user_data):
    note = notes[0]

    client.post(f"{url}/{note.id}/view", params={"service_id": 1})
    response = client.post(f"{url}/{note.id}/view", params={"service_id": 1})
    assert response.status_code == status.HTTP_200_OK

    view = (
        dbsession.query(NoteView)
        .filter(NoteView.note_id == note.id, NoteView.user_id == authlib_user_data["id"])
        .one_or_none()
    )
    assert view.shown_count == 2

    dbsession.delete(view)
    dbsession.commit()


def test_nonexistent_note_returns_404(client):
    response = client.post(f"{url}/999999/view", params={"service_id": 1})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_archived_note_returns_403(client, notes):
    archived_note = notes[3]

    response = client.post(f"{url}/{archived_note.id}/view", params={"service_id": 1})
    assert response.status_code == status.HTTP_403_FORBIDDEN
