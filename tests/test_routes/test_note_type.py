import pytest
from starlette import status

from modal_backend.models import NoteType
from modal_backend.schemas.models import NoteTypeGet
from modal_backend.settings import get_settings

url: str = "/notificationtype"
settings = get_settings()


@pytest.mark.parametrize(
    "status_code",
    [
        (status.HTTP_200_OK),
    ],
)
def test_get_notification_type(client, dbsession, note_types, status_code):
    response = client.get(url)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "status_code, body",
    [
        (
            status.HTTP_200_OK,
            {
                "type_id": 4,
                "name": "No_exist_type",
            },
        ),
        (
            status.HTTP_409_CONFLICT,
            {
                "type_id": 1,
                "name": "Already_exist_type",
            },
        ),
        (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            {
                "type_id": -100,
                "name": "string",
            },
        ),
        (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            {
                "type_id": 4,
                "name": 123,
            },
        ),
        (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            {
                "type_id": "string",
                "name": "string",
            },
        ),
        (
            status.HTTP_409_CONFLICT,
            {
                "type_id": 3,
                "name": "NoteType with is_deleted=True",
            },
        ),
    ],
)
def test_post_create_notification_type(client, dbsession, note_types, status_code, body):
    response = client.post(url, json=body)
    assert response.status_code == status_code

    if status_code == status.HTTP_200_OK:
        response_model = NoteTypeGet(**response.json())
        exist_note_type = dbsession.query(NoteType).filter(NoteType.type_id == response_model.type_id).one_or_none()
        assert exist_note_type
        assert exist_note_type.name == body.get("name")
        assert exist_note_type.type_id == body.get("type_id")
