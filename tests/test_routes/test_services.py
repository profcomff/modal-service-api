import pytest
from starlette import status

from modal_backend.models import Service
from modal_backend.schemas.models import ServiceGet
from modal_backend.settings import get_settings

url: str = "/service"
settings = get_settings()


@pytest.mark.parametrize(
    "status_code, body",
    [
        (status.HTTP_200_OK, {"service_id": 4, "name": "Service_3"}),
        (status.HTTP_409_CONFLICT, {"service_id": 2, "name": "Service_2"}),
        (status.HTTP_422_UNPROCESSABLE_CONTENT, {"service_id": "abc", "name": "Service_2"}),
        (status.HTTP_422_UNPROCESSABLE_CONTENT, {"service_id": 4, "name": 123}),
    ],
)
def test_post_service(client, dbsession, services, status_code, body):
    response = client.post(url, json=body)
    assert response.status_code == status_code

    if status_code == status.HTTP_200_OK:
        response_data = response.json()
        response_model = ServiceGet(**response_data)
        exist_service = Service.query(session=dbsession).filter(Service.id == response_model.id).one_or_none()
        assert exist_service
        try:
            assert exist_service.service_id == body.get("service_id")
            assert exist_service.name == body.get("name")
        finally:
            dbsession.delete(exist_service)
            dbsession.commit()


@pytest.mark.parametrize(
    "status_code",
    [
        (status.HTTP_200_OK),
    ],
)
def test_get_services(client, status_code):
    response = client.get(url)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "status_code, body, service_n",
    [
        (
            status.HTTP_200_OK,
            {"service_id": 999, "name": "New_service_name"},
            1,
        ),
        (
            status.HTTP_200_OK,
            {"service_id": 2, "name": "New_service_name"},
            1,
        ),
        (
            status.HTTP_200_OK,
            {"service_id": 999, "name": "Service_2"},
            1,
        ),
        (
            status.HTTP_404_NOT_FOUND,
            {"service_id": 1, "name": "New_service_name"},
            999,
        ),
        (
            status.HTTP_409_CONFLICT,
            {"service_id": 2, "name": "Service_2"},
            1,
        ),
        (
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            {"service_id": "abc", "name": "Service_2"},
            1,
        ),
        (
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            {"service_id": 2, "name": 999},
            1,
        ),
    ],
)
def test_update_service(client, dbsession, services, status_code, body, service_n):
    service_indexes = list(range(len(services)))
    response = client.patch(f"{url}/{services[service_n].id if service_n in service_indexes else service_n}", json=body)
    assert response.status_code == status_code

    if status_code == status.HTTP_200_OK:
        response_model = ServiceGet.model_validate(response.json(), extra="forbid")
        exist_service = (
            Service.query(session=dbsession).filter(Service.id == response_model.id).populate_existing().one_or_none()
        )
        assert exist_service
        assert exist_service.service_id == body.get("service_id")
        assert exist_service.name == body.get("name")


@pytest.mark.parametrize(
    "status_code, service_n",
    [
        (
            status.HTTP_200_OK,
            1,
        ),
        (
            status.HTTP_404_NOT_FOUND,
            999,
        ),
        (
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "abc",
        ),
    ],
)
def test_delete_service(client, dbsession, services, status_code, service_n):
    service_indexes = list(range(len(services)))
    response = client.delete(f"{url}/{services[service_n].id if service_n in service_indexes else service_n}")
    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        none_exist_service = (
            dbsession.query(Service).filter(Service.id == services[service_n].id).populate_existing().one_or_none()
        )
        assert none_exist_service.is_deleted
