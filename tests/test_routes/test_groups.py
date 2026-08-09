import pytest
from starlette import status

from modal_backend.models import Group
from modal_backend.schemas.models import GroupGet
from modal_backend.settings import get_settings

url: str = "/group"
settings = get_settings()


@pytest.mark.parametrize(
    "status_code, body",
    [
        (status.HTTP_200_OK, {"group_id": 4, "name": "Group_3"}),
        (status.HTTP_409_CONFLICT, {"group_id": 2, "name": "Group_2"}),
        (status.HTTP_422_UNPROCESSABLE_CONTENT, {"group_id": "abc", "name": "Group_2"}),
        (status.HTTP_422_UNPROCESSABLE_CONTENT, {"group_id": 4, "name": 123}),
    ],
)
def test_post_group(client, dbsession, groups, status_code, body):
    response = client.post(url, json=body)
    assert response.status_code == status_code

    if status_code == status.HTTP_200_OK:
        response_data = response.json()
        response_model = GroupGet(**response_data)
        exist_group = Group.query(session=dbsession).filter(Group.id == response_model.id).one_or_none()
        assert exist_group
        try:
            assert exist_group.group_id == body.get("group_id")
            assert exist_group.name == body.get("name")
        finally:
            dbsession.delete(exist_group)
            dbsession.commit()


@pytest.mark.parametrize(
    "status_code",
    [
        (status.HTTP_200_OK),
    ],
)
def test_get_groups(client, status_code):
    response = client.get(url)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "status_code, body, group_n",
    [
        (
            status.HTTP_200_OK,
            {"group_id": 999, "name": "New_group_name"},
            1,
        ),
        (
            status.HTTP_200_OK,
            {"group_id": 2, "name": "New_group_name"},
            1,
        ),
        (
            status.HTTP_200_OK,
            {"group_id": 999, "name": "Group_2"},
            1,
        ),
        (
            status.HTTP_404_NOT_FOUND,
            {"group_id": 1, "name": "New_group_name"},
            999,
        ),
        (
            status.HTTP_409_CONFLICT,
            {"group_id": 2, "name": "Group_2"},
            1,
        ),
        (
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            {"group_id": "abc", "name": "Group_2"},
            1,
        ),
        (
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            {"group_id": 2, "name": 999},
            1,
        ),
    ],
)
def test_update_group(client, dbsession, groups, status_code, body, group_n):
    group_indexes = list(range(len(groups)))
    response = client.patch(f"{url}/{groups[group_n].id if group_n in group_indexes else group_n}", json=body)
    assert response.status_code == status_code

    if status_code == status.HTTP_200_OK:
        response_data = response.json()
        response_model = GroupGet(**response_data)
        exist_group = (
                Group.query(session=dbsession).filter(Group.id == response_model.id).populate_existing().one_or_none()
                )
        assert exist_group
        assert exist_group.group_id == body.get("group_id")
        assert exist_group.name == body.get("name")


@pytest.mark.parametrize(
    "status_code, group_n",
    [
        (status.HTTP_200_OK, 1,),
        (status.HTTP_404_NOT_FOUND, 99,),
        (status.HTTP_422_UNPROCESSABLE_CONTENT, "abc",),
    ],
)
def test_delete_group(client, dbsession, groups, status_code, group_n):
    group_indexes = list(range(len(groups)))
    response = client.delete(f"{url}/{groups[group_n].id if group_n in group_indexes else group_n}")
    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        none_exist_group = (
            dbsession.query(Group).filter(Group.id == groups[group_n].id).populate_existing().one_or_none()
        )
        assert none_exist_group.is_deleted
