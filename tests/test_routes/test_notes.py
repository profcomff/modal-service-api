import pytest
from starlette import status

from modal_backend.models.db import Note, Group, Service, ModalStatus
from modal_backend.schemas.models import NoteInfoGet, NoteRatingGet, NoteTextGet, NoteChoiceGet, NoteImageGet
from modal_backend.settings import get_settings

url: str = "/notification"
settings = get_settings()


@pytest.mark.parametrize(
    "status_code, type_id, group_n_list, service_n_list, modal_status, asc_order, limit, offset, len_without_confines",
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
            7,  # len_without_confines
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
            2,  # len_without_confines
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
            4,  # len_without_confines
        ),
        (  # ограничение по группам и сервисам
            status.HTTP_404_NOT_FOUND,
            None,  # type_id
            [0, 1],  # group_n_list
            [2],  # service_n_list
            None,  # modal_status
            None,  # asc_order
            None,  # limit
            None,  # offset
            0,  # len_without_confines
        ),
        (  # ограничение по типу модалки
            status.HTTP_200_OK,
            4,  # type_id
            None,  # group_n_list
            None,  # service_n_list
            None,  # modal_status
            None,  # asc_order
            None,  # limit
            None,  # offset
            1,  # len_without_confines
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
            0,  # len_without_confines
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
            0,  # len_without_confines
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
            0,  # len_without_confines
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
            0,  # len_without_confines
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
            0,  # len_without_confines
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
            0,  # len_without_confines
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
            0,  # len_without_confines
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
            0,  # len_without_confines
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
            0,  # len_without_confines
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
            0,  # len_without_confines
        ),
    ],
)
def test_get_notes(
    client,
    dbsession,
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
    len_without_confines,
):
    # Добавление id групп и сервисов с проверкой типа, чтобы можно было указать не валидные query-параметры.
    group_indexes = range(len(groups))
    service_indexes = range(len(services))
    groups_id = []
    services_id = []
    if isinstance(group_n_list, list): 
        for group_n in group_n_list:
            if group_n in group_indexes:
                groups_id.append(groups[group_n].id)
            else:
                groups_id.append(group_n)
    else:
        groups_id = group_n_list

    if isinstance(service_n_list, list): 
        for service_n in service_n_list:
            if service_n in service_indexes:
                services_id.append(services[service_n].id)
            else:
                services_id.append(service_n)
    else:
        services_id = service_n_list
 
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
        response_objs_by_id = Note.query(session=dbsession).filter(
            Note.id.in_([note.get("id") for note in response_data])
        )
        assert len(response_data) != 0

        get_limit = query.get("limit", 10)
        get_offset = query.get("offset", 0)
        # проверка лимита
        assert len(response_data) <= get_limit
        # проверка смещения и нормальной длины без лимита и без лимита и смещения
        if len_without_confines < get_limit:
            assert (
                len(response_data) == len_without_confines - get_offset if get_offset < len_without_confines else 0
            ), f"response_data={len(response_data)} != expr={len_without_confines - get_offset if get_offset < len_without_confines else 0}"
        elif len_without_confines > get_limit:
            assert (
                len(response_data) == get_limit - get_offset if get_offset < get_limit else 0
            ), f"response_data={len(response_data)} != expr={get_limit - get_offset if get_offset < get_limit else 0}"

        # проверяем порядок
        check_order = query.get("asc_order", False)
        reverse_key = False if check_order else True

        ts_data = sorted([obj.start_ts for obj in response_objs_by_id], reverse=reverse_key)
        compare = (lambda x, y: x >= y) if check_order is False else (lambda x, y: x <= y)
        assert all(compare(x, y) for x, y in zip(ts_data, ts_data[1:]))

        # проверка корректности данных отфильтрованных модалок
        if type_id:
            for resp_obj in response_data:
                assert resp_obj.get("type_id") == type_id
        if modal_status:
            for resp_obj in response_data:
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

    ]
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
            False
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
        (# просроченная модалка
            status.HTTP_403_FORBIDDEN,
            5,
            ModalStatus.ACTIVE,
            False,
            False,
        ),
        (# просроченная модалка с is_always=True
            status.HTTP_200_OK,
            6,
            ModalStatus.ACTIVE,
            False,
            False,
        ),

    ]
)
def test_update_note_status(client, dbsession, notes, note_n, status_code, modal_status, deleted_group_id_flag, deleted_service_id_flag):

    notes_indexes = range(len(notes))
    id_of_note = notes[note_n].id if note_n in notes_indexes else note_n

    if deleted_group_id_flag:
        for group_id in notes[note_n].group_ids:
            group = Group.query(session=dbsession).filter(Group.id == group_id).first()
            dbsession.delete(group)
        dbsession.commit()
    if deleted_service_id_flag:
        for service_id in notes[note_n].service_ids:
            service = Service.query(session=dbsession).filter(Service.id == service_id).first()
            dbsession.delete(service)
        dbsession.commit()

    response = client.patch(f"{url}/{id_of_note}/status")
    assert response.status_code == status_code

    if status_code == status.HTTP_200_OK:
        response_data = response.json()
        note = Note.query(session=dbsession).filter(Note.id == response_data.get("id")).populate_existing().first()
        assert note.status == modal_status


    
    
 
