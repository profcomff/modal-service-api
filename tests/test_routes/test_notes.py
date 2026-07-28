import pytest
from starlette import status

from modal_backend.settings import get_settings
from modal_backend.schemas.models import NoteGet
from modal_backend.models.db import Note

url: str = "/notification"
settings = get_settings()


@pytest.mark.parametrize(
        "status_code, type_id, groups_id, services_id, modal_status, asc_order, limit, offset, len_without_confines", 
    [   
     # позитивные кейсы(объединенные проверки)
        (# все модалки
            status.HTTP_200_OK,
            None,      # type_id    
            None,      # groups_id
            None,      # services_id
            None,      # modal_status
            None,      # asc_order
            None,      # limit
            None,      # offset 
            5,         # len_without_confines
        ),
        (# активные - ограничение по лимиту и смещению + порядок + группы
            status.HTTP_200_OK,
            None,      # type_id    
            [3],      # groups_id
            [3],      # services_id
            "active",      # modal_status
            True,      # asc_order
            2,      # limit
            1,      # offset 
            2,         # len_without_confines

        ),
        (# архив - ограничение по лимиту и смещению + порядок
            status.HTTP_200_OK,
            None,      # type_id    
            [1, 2, 3],      # groups_id
            [1, 2, 3],      # services_id
            "archived",      # modal_status
            False,      # asc_order
            999,      # limit
            1,      # offset 
            2,         # len_without_confines

        ),
        (# ограничение по группам и сервисам
            status.HTTP_404_NOT_FOUND,
            None,      # type_id    
            [1, 2],      # groups_id
            [3],      # services_id
            None,      # modal_status
            None,      # asc_order
            None,      # limit
            None,      # offset 
            0,         # len_without_confines

        ),
        (# ограничение по типу модалки
            status.HTTP_200_OK,
            4,      # type_id    
            None,      # groups_id
            None,      # services_id
            None,      # modal_status
            None,      # asc_order
            None,      # limit
            None,      # offset 
            1,         # len_without_confines
        ),
        (# нулевой лимит
            status.HTTP_404_NOT_FOUND,
            None,      # type_id    
            None,      # groups_id
            None,      # services_id
            None,      # modal_status
            None,      # asc_order
            0,      # limit
            None,      # offset 
            0,         # len_without_confines
        ),
        (# отрицательный лимит + не валидный лимит
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            None,     # type_id    
            None,    # groups_id
            None,      # services_id
            None,      # modal_status
            None,      # asc_order
            -1,      # limit
            None,      # offset 
            0,         # len_without_confines
        ),
        (# отрицательное смещение + не валидное смещение
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            None,     # type_id    
            None,    # groups_id
            None,      # services_id
            None,      # modal_status
            None,      # asc_order
            None,      # limit
            -1,      # offset 
            0,         # len_without_confines
        ),
        (# offset превышающее lwc и limit
            status.HTTP_404_NOT_FOUND,
            None,      # type_id    
            None,      # groups_id
            None,      # services_id
            None,      # modal_status
            None,      # asc_order
            4,      # limit
            999,      # offset 
            0,         # len_without_confines
        ),
        (# не существующий type_id
            status.HTTP_404_NOT_FOUND,
            999,      # type_id    
            None,      # groups_id
            None,      # services_id
            None,      # modal_status
            None,      # asc_order
            None,      # limit
            None,      # offset 
            0,         # len_without_confines
        ),
        (# не валидный type_id
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "abc",      # type_id    
            None,      # groups_id
            None,      # services_id
            None,      # modal_status
            None,      # asc_order
            None,      # limit
            None,      # offset 
            0,         # len_without_confines
        ),
        (# не валидные groups_id
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            None,     # type_id    
            [1, "two", 3],    # groups_id
            None,      # services_id
            None,      # modal_status
            None,      # asc_order
            None,      # limit
            None,      # offset 
            0,         # len_without_confines
        ),
        (# не валидные service_ids
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            None,     # type_id    
            None,    # groups_id
            [1, "two", 3],      # services_id
            None,      # modal_status
            None,      # asc_order
            None,      # limit
            None,      # offset 
            0,         # len_without_confines
        ),
        (# не валидный status
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            None,     # type_id    
            None,    # groups_id
            None,      # services_id
            999,      # modal_status
            None,      # asc_order
            None,      # limit
            None,      # offset 
            0,         # len_without_confines
        ),
        (# не валидные asc_order
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            None,     # type_id    
            None,    # groups_id
            None,      # services_id
            None,      # modal_status
            999,      # asc_order
            None,      # limit
            None,      # offset 
            0,         # len_without_confines
        ),
    ]
)
def test_get_notes(client, 
                   dbsession,
                   notes,
                   status_code,
                   type_id,
                   groups_id,
                   services_id,
                   modal_status,
                   asc_order,
                   limit,
                   offset,
                   len_without_confines):
    dict_of_params = {"type_id" : type_id if type_id is not None else None,
                      "groups_id" : groups_id if groups_id is not None else None,
                      "services_id" : services_id if services_id is not None else None,
                      "status" : modal_status if modal_status is not None else None,
                      "asc_order" : asc_order if asc_order is not None else None,
                      "limit" : limit if limit is not None else None,
                      "offset" : offset if offset is not None else None,
                      }
    query = {k : v for k, v in dict_of_params.items() if v is not None}
    response = client.get(url, params=query)

    assert response.status_code == status_code
    
    if status_code == status.HTTP_200_OK:
        response_data = response.json()
        response_objs_by_id = Note.query(session=dbsession).filter(Note.id.in_([note.get("id") for note in response_data]))
        assert len(response_data) != 0

        get_limit = query.get("limit", 10)
        get_offset = query.get("offset", 0)
        # проверка лимита
        assert len(response_data) <= get_limit
        # проверка смещения и нормальной длины без лимита и без лимита и смещения
        if len_without_confines < get_limit:
            assert len(response_data) == len_without_confines - get_offset if get_offset < len_without_confines else 0, f"response_data={len(response_data)} != expr={len_without_confines - get_offset if get_offset < len_without_confines else 0}"
        elif len_without_confines > get_limit:
            assert len(response_data) == get_limit - get_offset if get_offset < get_limit else 0, f"response_data={len(response_data)} != expr={get_limit - get_offset if get_offset < get_limit else 0}" 

        
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



 
        

