import pytest
from starlette import status

from modal_backend.models.db import NoteView

url = "/user"


@pytest.fixture()
def note_view_cleanup(dbsession, authlib_user_data):
    yield
    dbsession.query(NoteView).filter(NoteView.user_id == authlib_user_data["id"]).delete()
    dbsession.commit()


@pytest.mark.parametrize(
    "note_index, view_count, expected_status, expected_shown_count",
    [
        pytest.param(0, 1, status.HTTP_200_OK, 1, id="first_view_creates_note_view"),
        pytest.param(0, 2, status.HTTP_200_OK, 2, id="second_view_increments_shown_count"),
        pytest.param(None, 1, status.HTTP_404_NOT_FOUND, None, id="nonexistent_note_returns_404"),
        pytest.param(3, 1, status.HTTP_403_FORBIDDEN, None, id="archived_note_returns_403"),
    ],
)
def test_mark_note_view(
    client,
    dbsession,
    notes,
    services,
    authlib_user_data,
    note_view_cleanup,
    note_index,
    view_count,
    expected_status,
    expected_shown_count,
):
    note_id = notes[note_index].id if note_index is not None else 999999
    service_id = services[0].service_id

    for _ in range(view_count):
        response = client.post(f"{url}/{note_id}/view", params={"service_id": service_id})
    assert response.status_code == expected_status

    if expected_shown_count is not None:
        view = (
            dbsession.query(NoteView)
            .filter(NoteView.note_id == note_id, NoteView.user_id == authlib_user_data["id"])
            .one_or_none()
        )
        assert view is not None
        assert view.shown_count == expected_shown_count
