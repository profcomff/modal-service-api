from datetime import datetime, timezone

import pytest
from starlette import status

from modal_backend.models.db import NoteResponse
from modal_backend.schemas.models import NoteResponseChoiceGet, NoteResponseRatingGet, NoteResponseTextGet

url: str = "/notification"


@pytest.mark.parametrize(
    "status_code, note_index, response_data, response_model, response_field, response_value, absent_fields",
    [
        (
            status.HTTP_200_OK,
            1,
            {"rating": 5},
            NoteResponseRatingGet,
            "rating",
            5,
            {"text", "selected_choices"},
        ),
        (
            status.HTTP_200_OK,
            2,
            {"text": "Тестовый ответ"},
            NoteResponseTextGet,
            "text",
            "Тестовый ответ",
            {"rating", "selected_choices"},
        ),
        (
            status.HTTP_200_OK,
            3,
            {"selected_choices": [{"id": 1, "text": "Да"}]},
            NoteResponseChoiceGet,
            "selected_choices",
            [{"id": 1, "text": "Да"}],
            {"rating", "text"},
        ),
    ],
)
def test_get_note_responses_by_note_type(
    client,
    dbsession,
    notes,
    status_code,
    note_index,
    response_data,
    response_model,
    response_field,
    response_value,
    absent_fields,
):
    note = notes[note_index]
    note_response = NoteResponse(
        note_id=note.id,
        user_id=101,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        **response_data,
    )
    dbsession.add(note_response)
    dbsession.commit()

    try:
        response = client.get(f"{url}/{note.id}/responses")
        assert response.status_code == status_code

        response_data = response.json()
        assert len(response_data) == 1
        response_model.model_validate(response_data[0], extra="forbid")
        response_item = response_data[0]
        assert response_item[response_field] == response_value
        assert absent_fields.isdisjoint(response_item)
        assert all(value is not None for value in response_item.values())
    finally:
        dbsession.delete(note_response)
        dbsession.commit()


@pytest.mark.parametrize("note_index", [0, 4])
def test_get_note_responses_returns_empty_for_info_and_image(client, dbsession, notes, note_index):
    note = notes[note_index]
    note_response = NoteResponse(
        note_id=note.id,
        user_id=101,
        text="Ответ не должен возвращаться",
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    dbsession.add(note_response)
    dbsession.commit()

    try:
        response = client.get(f"{url}/{note.id}/responses")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    finally:
        dbsession.delete(note_response)
        dbsession.commit()


@pytest.mark.parametrize(
    "status_code, limit, offset",
    [
        (status.HTTP_200_OK, 1, 1),
        (status.HTTP_200_OK, 10, 0),
        (status.HTTP_200_OK, 0, 0),
        (status.HTTP_422_UNPROCESSABLE_CONTENT, -1, 0),
        (status.HTTP_422_UNPROCESSABLE_CONTENT, 10, -1),
    ],
)
def test_get_note_responses_limit_and_offset(client, dbsession, notes, status_code, limit, offset):
    note = notes[2]
    note_responses = [
        NoteResponse(
            note_id=note.id,
            user_id=user_id,
            text=f"Ответ {user_id}",
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        for user_id in [101, 102, 103]
    ]
    dbsession.add_all(note_responses)
    dbsession.commit()

    try:
        response = client.get(f"{url}/{note.id}/responses", params={"limit": limit, "offset": offset})
        assert response.status_code == status_code

        if status_code == status.HTTP_200_OK:
            response_data = response.json()
            assert len(response_data) == min(limit, max(0, len(note_responses) - offset))
            for response_item in response_data:
                NoteResponseTextGet.model_validate(response_item, extra="forbid")
    finally:
        for note_response in note_responses:
            dbsession.delete(note_response)
        dbsession.commit()
