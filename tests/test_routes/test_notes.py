from typing import Any

import pytest
from starlette import status

from modal_backend.models.db import Group, ModalStatus, Note, NoteTypeEnum, Service
from modal_backend.schemas.models import NoteChoiceGet, NoteImageGet, NoteInfoGet, NoteRatingGet, NoteTextGet
from modal_backend.settings import get_settings

url: str = "/notification"
settings = get_settings()


def resolve_items(n_list: list | Any, items: list) -> list | Any:
    """
    Вспомогательная функция для перевода индексов списков групп и сервисов
    с учётом возможности указывать невалидные значения(для негативных кейсов)
    """
    indexes = range(len(items))
    list_ids = []
    if isinstance(n_list, list):
        for n in n_list:
            if n in indexes:
                list_ids.append(items[n].id)
            else:
                list_ids.append(n)
    else:
        list_ids = n_list
    return list_ids


@pytest.mark.parametrize(
    "status_code, body, type_model, path",
    [
        (
            status.HTTP_200_OK,
            {
                "header": "string",
                "group_ids": [0],  # индексы
                "service_ids": [0],  # индексы
                "frequency": 0,
                "start_ts": "2026-08-04T17:21:45.694Z",
                "end_ts": "2026-08-04T17:22:45.694Z",
                "is_always": False,
                "info_text": "string",
            },
            NoteInfoGet,
            "/info",
        ),
        (
            status.HTTP_200_OK,
            {
                "header": "string",
                "group_ids": [0],  # индексы
                "service_ids": [0],  # индексы
                "frequency": 0,
                "start_ts": "2026-08-04T17:21:45.694Z",
                "end_ts": "2026-08-04T17:22:45.694Z",
                "is_always": True,
                "rating_max": 0,
            },
            NoteRatingGet,
            "/rating",
        ),
        (
            status.HTTP_200_OK,
            {
                "header": "string",
                "group_ids": [0],  # индексы
                "service_ids": [0],  # индексы
                "frequency": 0,
                "start_ts": "2026-08-04T17:21:45.694Z",
                "end_ts": "2026-08-04T17:22:45.694Z",
                "is_always": False,
                "text": "string",
                "max_length": 6,
            },
            NoteTextGet,
            "/text",
        ),
        (
            status.HTTP_200_OK,
            {
                "header": "string",
                "group_ids": [0],  # индексы
                "service_ids": [0],  # индексы
                "frequency": 0,
                "start_ts": "2026-08-04T17:21:45.694Z",
                "end_ts": "2026-08-04T17:22:45.694Z",
                "is_always": True,
                "choice_options": [{"id": 0, "text": "string"}],
                "is_multiple": True,
            },
            NoteChoiceGet,
            "/choice",
        ),
        (
            status.HTTP_200_OK,
            {
                "header": "string",
                "group_ids": [0],  # индексы
                "service_ids": [0],  # индексы
                "frequency": 0,
                "start_ts": "2026-08-04T17:21:45.694Z",
                "end_ts": "2026-08-04T17:22:45.694Z",
                "is_always": False,
                "images": ["string"],
            },
            NoteImageGet,
            "/image",
        ),
        (
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            {
                "header": "string",
                "group_ids": "two",  # индексы
                "service_ids": [1, "two", 3],  # индексы
                "frequency": "digit",
                "start_ts": "2026-08-04T17:21:45.694Z",
                "end_ts": "2026-08-04T17:22:45.694Z",
                "is_always": None,
                "info_text": "string",
            },
            NoteInfoGet,
            "/info",
        ),
        (
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            {
                "header": "string",
                "group_ids": "two",  # индексы
                "service_ids": [1, "two", 3],  # индексы
                "frequency": "digit",
                "start_ts": "2026-08-04T17:21:45.694Z",
                "end_ts": "2026-08-04T17:22:45.694Z",
                "is_always": None,
                "max_rating": "string",
            },
            NoteRatingGet,
            "/rating",
        ),
        (
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            {
                "header": "string",
                "group_ids": "two",  # индексы
                "service_ids": [1, "two", 3],  # индексы
                "frequency": "digit",
                "start_ts": "2026-08-04T17:21:45.694Z",
                "end_ts": "2026-08-04T17:22:45.694Z",
                "is_always": None,
                "text": "string",
                "max_length": "string",
            },
            NoteTextGet,
            "/text",
        ),
        (
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            {
                "header": "string",
                "group_ids": "two",  # индексы
                "service_ids": [1, "two", 3],  # индексы
                "frequency": "digit",
                "start_ts": "2026-08-04T17:21:45.694Z",
                "end_ts": "2026-08-04T17:22:45.694Z",
                "is_always": None,
                "choice_options": [{"id": 0, "text": "string"}],
                "is_multiple": None,
            },
            NoteChoiceGet,
            "/choice",
        ),
        (
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            {
                "header": "string",
                "group_ids": "two",  # индексы
                "service_ids": [1, "two", 3],  # индексы
                "frequency": "digit",
                "start_ts": "2026-08-04T17:21:45.694Z",
                "end_ts": "2026-08-04T17:22:45.694Z",
                "is_always": None,
                "images": ["string"],
            },
            NoteImageGet,
            "/image",
        ),
    ],
)
def test_create_all_type_of_note(client, dbsession, groups, services, status_code, body, type_model, path):

    json_body = body
    group_n_list = json_body.get("group_ids")
    service_n_list = json_body.get("service_ids")
    groups_id = resolve_items(group_n_list, groups)
    services_id = resolve_items(service_n_list, services)

    json_body["group_ids"] = groups_id
    json_body["service_ids"] = services_id

    response = client.post(f"{url}{path}", json=json_body)
    assert response.status_code == status_code

    if status_code == status.HTTP_200_OK:
        response_model = type_model.model_validate(response.json(), extra="forbid")
        note = Note.query(session=dbsession).filter(Note.id == response_model.id).one_or_none()
        assert note
        assert response_model.type_id == note.type_id
        assert response_model.header == note.header
        assert response_model.status == note.status
        assert response_model.admin_id == note.admin_id

        if type_model is NoteTextGet:
            assert len(note.text) <= note.max_length
        dbsession.delete(note)


def calculate_expected_len(
    all_notes,
    type_id: int | None,
    groups_id: list[int] | None,
    services_id: list[int] | None,
    status: str | None,
    limit: int,
    offset: int,
    asc_order: bool | None,
) -> list[Note]:
    """
    Вспомогательная функция для подсчета корректной длины списка модалок
    документирующая контракт пагинации и фильтрации
    в modal_backend/utils/service.py::NoteService.get_note_by_filters
    """
    filtered_notes = all_notes
    if type_id is not None:
        filtered_notes = [note for note in filtered_notes if note.type_id == type_id]
    if groups_id is not None:
        filtered_notes = [note for note in filtered_notes if any(g in note.group_ids for g in groups_id)]
    if services_id is not None:
        filtered_notes = [note for note in filtered_notes if any(s in note.service_ids for s in services_id)]
    if status is not None:
        filtered_notes = [note for note in filtered_notes if note.status == status]

    filtered_notes = sorted(filtered_notes, key=lambda note: note.start_ts, reverse=(asc_order is not True))

    return [note.id for note in filtered_notes[offset : limit + offset]]


@pytest.mark.parametrize(
    "status_code, type_id, group_n_list, service_n_list, modal_status, asc_order, limit, offset",
    [
        # позитивные кейсы(объединенные проверки)
        (  # все модалки
            status.HTTP_200_OK,
            None,  # type_id
            None,  # group_n_list
            None,  # service_n_list
            None,  # modal_status
            None,  # asc_order
            None,  # limit
            None,  # offset
        ),
        (  # активные - ограничение по лимиту и смещению + порядок + группы
            status.HTTP_200_OK,
            None,  # type_id
            [2],  # group_n_list
            [2],  # service_n_list
            "active",  # modal_status
            True,  # asc_order
            2,  # limit
            1,  # offset
        ),
        (  # архив - ограничение по лимиту и смещению + порядок
            status.HTTP_200_OK,
            None,  # type_id
            [0, 1, 2],  # group_n_list
            [0, 1, 2],  # service_n_list
            "archived",  # modal_status
            False,  # asc_order
            999,  # limit
            1,  # offset
        ),
        (
            status.HTTP_404_NOT_FOUND,
            None,  # type_id
            [0, 1, 2],  # group_n_list
            [0, 1, 2],  # service_n_list
            "archived",  # modal_status
            False,  # asc_order
            None,  # limit
            5,  # offset
        ),
        (  # ограничение по группам и сервисам
            status.HTTP_200_OK,
            None,  # type_id
            [0, 1],  # group_n_list
            [2],  # service_n_list
            None,  # modal_status
            None,  # asc_order
            None,  # limit
            None,  # offset
        ),
        (  # не существующие группы и сервисы
            status.HTTP_404_NOT_FOUND,
            None,  # type_id
            [4],  # group_n_list
            [4],  # service_n_list
            None,  # modal_status
            None,  # asc_order
            None,  # limit
            None,  # offset
        ),
        (  # ограничение по типу модалки
            status.HTTP_200_OK,
            NoteTypeEnum.CHOICE,  # type_id
            None,  # group_n_list
            None,  # service_n_list
            None,  # modal_status
            None,  # asc_order
            None,  # limit
            None,  # offset
        ),
        (  # нулевой лимит
            status.HTTP_404_NOT_FOUND,
            None,  # type_id
            None,  # group_n_list
            None,  # service_n_list
            None,  # modal_status
            None,  # asc_order
            0,  # limit
            None,  # offset
        ),
        # негативные кейсы
        (  # отрицательный лимит + не валидный лимит
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            None,  # type_id
            None,  # group_n_list
            None,  # service_n_list
            None,  # modal_status
            None,  # asc_order
            -1,  # limit
            None,  # offset
        ),
        (  # отрицательное смещение + не валидное смещение
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            None,  # type_id
            None,  # group_n_list
            None,  # service_n_list
            None,  # modal_status
            None,  # asc_order
            None,  # limit
            -1,  # offset
        ),
        (  # offset превышающее lwc и limit
            status.HTTP_404_NOT_FOUND,
            None,  # type_id
            None,  # group_n_list
            None,  # service_n_list
            None,  # modal_status
            None,  # asc_order
            4,  # limit
            999,  # offset
        ),
        (  # не существующий type_id
            status.HTTP_404_NOT_FOUND,
            999,  # type_id
            None,  # group_n_list
            None,  # service_n_list
            None,  # modal_status
            None,  # asc_order
            None,  # limit
            None,  # offset
        ),
        (  # не валидный type_id
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "abc",  # type_id
            None,  # group_n_list
            None,  # service_n_list
            None,  # modal_status
            None,  # asc_order
            None,  # limit
            None,  # offset
        ),
        (  # не валидные group_n_list
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            None,  # type_id
            "two",  # group_n_list
            None,  # service_n_list
            None,  # modal_status
            None,  # asc_order
            None,  # limit
            None,  # offset
        ),
        (  # не валидные service_ids
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            None,  # type_id
            None,  # group_n_list
            "two",  # service_n_list
            None,  # modal_status
            None,  # asc_order
            None,  # limit
            None,  # offset
        ),
        (  # не валидный status
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            None,  # type_id
            None,  # group_n_list
            None,  # service_n_list
            999,  # modal_status
            None,  # asc_order
            None,  # limit
            None,  # offset
        ),
        (  # не валидные asc_order
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            None,  # type_id
            None,  # group_n_list
            None,  # service_n_list
            None,  # modal_status
            999,  # asc_order
            None,  # limit
            None,  # offset
        ),
    ],
)
def test_get_notes(
    client,
    notes,
    groups,
    services,
    status_code,
    type_id,
    group_n_list,
    service_n_list,
    modal_status,
    asc_order,
    limit,
    offset,
):
    # Добавление id групп и сервисов с проверкой типа, чтобы можно было указать не валидные query-параметры.
    groups_id = resolve_items(group_n_list, groups)
    services_id = resolve_items(service_n_list, services)

    dict_of_params = {
        "type_id": type_id if type_id is not None else None,
        "groups_id": groups_id if groups_id is not None else None,
        "services_id": services_id if services_id is not None else None,
        "status": modal_status if modal_status is not None else None,
        "asc_order": asc_order if asc_order is not None else None,
        "limit": limit if limit is not None else None,
        "offset": offset if offset is not None else None,
    }
    query = {k: v for k, v in dict_of_params.items() if v is not None}
    response = client.get(url, params=query)

    assert response.status_code == status_code

    if status_code == status.HTTP_200_OK:
        response_data = response.json()

        ids_in_response = [note.get("id") for note in response_data]
        # проверяем порядок
        start_ts_by_id = {note.id: note.start_ts for note in notes}
        ts_data = [start_ts_by_id[note_id] for note_id in ids_in_response]
        if query.get("asc_order"):
            assert ts_data == sorted(ts_data)
        else:
            assert ts_data == sorted(ts_data, reverse=True)

        # проверка контракта фильтрации и пагинации(содержимого и длины после урезания limit-ом и offset-ом)
        expected_note_ids = calculate_expected_len(
            notes,
            type_id=query.get("type_id"),
            groups_id=query.get("groups_id"),
            services_id=query.get("services_id"),
            status=query.get("status"),
            limit=query.get("limit", 10),
            offset=query.get("offset", 0),
            asc_order=query.get("asc_order"),
        )

        assert ids_in_response == expected_note_ids
        # проверка корректности данных отфильтрованных модалок
        for resp_obj in response_data:
            if type_id:
                assert resp_obj.get("type_id") == type_id
            if modal_status:
                assert resp_obj.get("status") == modal_status


@pytest.mark.parametrize(
    "status_code, note_n, type_model",
    [
        (
            status.HTTP_200_OK,
            0,
            NoteInfoGet,
        ),
        (
            status.HTTP_200_OK,
            1,
            NoteRatingGet,
        ),
        (
            status.HTTP_200_OK,
            2,
            NoteTextGet,
        ),
        (
            status.HTTP_200_OK,
            3,
            NoteChoiceGet,
        ),
        (
            status.HTTP_200_OK,
            4,
            NoteImageGet,
        ),
        (
            status.HTTP_404_NOT_FOUND,
            -1,
            None,
        ),
        (
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "abc",
            None,
        ),
    ],
)
def test_get_note_by_id(client, notes, status_code, note_n, type_model):
    notes_indexes = range(len(notes))
    id_of_note = notes[note_n].id if note_n in notes_indexes else note_n
    response = client.get(f"{url}/{id_of_note}")

    assert response.status_code == status_code

    if status_code == status.HTTP_200_OK:
        type_model.model_validate(response.json(), extra="forbid")


@pytest.mark.parametrize(
    "status_code, note_n, modal_status, deleted_group_id_flag, deleted_service_id_flag",
    [
        (
            status.HTTP_200_OK,
            0,
            ModalStatus.ARCHIVED,
            False,
            False,
        ),
        (
            status.HTTP_404_NOT_FOUND,
            -1,
            ModalStatus.ACTIVE,
            False,
            False,
        ),
        (
            status.HTTP_200_OK,
            3,
            ModalStatus.ACTIVE,
            False,
            False,
        ),
        (
            status.HTTP_403_FORBIDDEN,
            3,
            ModalStatus.ACTIVE,
            True,
            False,
        ),
        (
            status.HTTP_403_FORBIDDEN,
            3,
            ModalStatus.ACTIVE,
            False,
            True,
        ),
        (
            status.HTTP_403_FORBIDDEN,
            3,
            ModalStatus.ACTIVE,
            True,
            True,
        ),
        (
            status.HTTP_403_FORBIDDEN,
            6,
            ModalStatus.ACTIVE,
            False,
            False,
        ),  # просроченная модалка
        (
            status.HTTP_200_OK,
            7,
            ModalStatus.ACTIVE,
            False,
            False,
        ),  # просроченная модалка с is_always=True
    ],
)
def test_update_note_status(
    client,
    dbsession,
    mock_datetime_now,
    notes,
    note_n,
    status_code,
    modal_status,
    deleted_group_id_flag,
    deleted_service_id_flag,
):

    notes_indexes = range(len(notes))
    id_of_note = notes[note_n].id if note_n in notes_indexes else note_n

    if deleted_group_id_flag:
        for group_id in notes[note_n].group_ids:
            group = Group.query(session=dbsession).filter(Group.id == group_id).one()
            group.is_deleted = True
        dbsession.commit()
    if deleted_service_id_flag:
        for service_id in notes[note_n].service_ids:
            service = Service.query(session=dbsession).filter(Service.id == service_id).one()
            service.is_deleted = True
        dbsession.commit()

    response = client.patch(f"{url}/{id_of_note}/status")
    assert response.status_code == status_code

    if status_code == status.HTTP_200_OK:
        response_data = response.json()
        note = Note.query(session=dbsession).filter(Note.id == response_data.get("id")).populate_existing().one()
        assert note.status == modal_status


@pytest.mark.parametrize(
    "status_code, note_n",
    [
        (status.HTTP_200_OK, 0),
        (status.HTTP_404_NOT_FOUND, -1),
        (status.HTTP_422_UNPROCESSABLE_CONTENT, "one"),
    ],
)
def test_delete_note(client, dbsession, notes, status_code, note_n):
    note_indexes = range(len(notes))
    id_of_note = notes[note_n].id if note_n in note_indexes else note_n

    response = client.delete(f"{url}/{id_of_note}")
    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        deleted_note = dbsession.query(Note).filter(Note.id == id_of_note).populate_existing().one_or_none()
        assert deleted_note.is_deleted
