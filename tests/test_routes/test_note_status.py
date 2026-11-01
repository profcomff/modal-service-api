"""Regression tests for issue #34: separate archive/restore endpoints."""

import pytest
from starlette import status

from modal_backend.models.db import Group, ModalStatus, Note, Service

URL = "/notification"


def note_id(notes, index):
    return notes[index].id if isinstance(index, int) and 0 <= index < len(notes) else index


def fresh_note(dbsession, id):
    return Note.query(session=dbsession).filter(Note.id == id).populate_existing().one()


@pytest.mark.parametrize(
    "index, expected_status",
    [
        (0, status.HTTP_200_OK),
        (3, status.HTTP_409_CONFLICT),
        (-1, status.HTTP_404_NOT_FOUND),
        ("invalid", status.HTTP_422_UNPROCESSABLE_CONTENT),
    ],
)
def test_archive(client, dbsession, notes, index, expected_status):
    id = note_id(notes, index)
    response = client.post(f"{URL}/{id}/archive")
    assert response.status_code == expected_status
    if expected_status == status.HTTP_409_CONFLICT:
        assert response.json()["ru"] == "Модалка уже в архиве"
        assert response.json()["message"] == "Notification is already archived"
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {"id": id, "status": ModalStatus.ARCHIVED.value}
        assert fresh_note(dbsession, id).status == ModalStatus.ARCHIVED


@pytest.mark.parametrize(
    "index, expected_status, delete_groups, delete_services",
    [
        (3, status.HTTP_200_OK, False, False),
        (0, status.HTTP_409_CONFLICT, False, False),
        (-1, status.HTTP_404_NOT_FOUND, False, False),
        ("invalid", status.HTTP_422_UNPROCESSABLE_CONTENT, False, False),
        (3, status.HTTP_403_FORBIDDEN, True, False),
        (3, status.HTTP_403_FORBIDDEN, False, True),
        (3, status.HTTP_403_FORBIDDEN, True, True),
        (6, status.HTTP_403_FORBIDDEN, False, False),  # expired
        (7, status.HTTP_200_OK, False, False),  # expired but is_always=True
    ],
)
def test_restore(client, dbsession, mock_datetime_now, notes, index, expected_status, delete_groups, delete_services):
    id = note_id(notes, index)
    if delete_groups:
        (
            dbsession.query(Group)
            .filter(Group.group_id.in_(notes[index].group_ids))
            .update({Group.is_deleted: True}, synchronize_session=False)
        )
    if delete_services:
        (
            dbsession.query(Service)
            .filter(Service.service_id.in_(notes[index].service_ids))
            .update({Service.is_deleted: True}, synchronize_session=False)
        )
    if delete_groups or delete_services:
        dbsession.commit()

    response = client.post(f"{URL}/{id}/restore")
    assert response.status_code == expected_status
    if expected_status == status.HTTP_409_CONFLICT:
        assert response.json()["ru"] == "Модалка уже активна"
        assert response.json()["message"] == "Notification is already active"
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {
            "id": id,
            "status": ModalStatus.ACTIVE.value,
            "removed_group_ids": [],
            "removed_service_ids": [],
        }
        assert fresh_note(dbsession, id).status == ModalStatus.ACTIVE
    elif isinstance(index, int) and index in (3, 6):
        assert fresh_note(dbsession, id).status == ModalStatus.ARCHIVED


def test_restore_filters_removed_external_ids(client, dbsession, mock_datetime_now, notes, groups, services):
    original = notes[5]
    removed_group_id = groups[1].group_id
    removed_service_id = services[2].service_id
    groups[1].is_deleted = True
    services[2].is_deleted = True
    dbsession.commit()

    response = client.post(f"{URL}/{original.id}/restore")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": original.id,
        "status": ModalStatus.ACTIVE.value,
        "removed_group_ids": [removed_group_id],
        "removed_service_ids": [removed_service_id],
    }
    restored = fresh_note(dbsession, original.id)
    assert restored.group_ids == [groups[0].group_id, groups[2].group_id]
    assert restored.service_ids == [services[0].service_id, services[1].service_id]


def test_restore_uses_external_ids_not_primary_keys(client, dbsession, mock_datetime_now, notes, groups, services):
    original = notes[3]
    groups[0].group_id = groups[0].id + 10_000
    groups[1].group_id = groups[1].id + 10_000
    services[0].service_id = services[0].id + 20_000
    services[1].service_id = services[1].id + 20_000
    original.group_ids = [groups[0].group_id, groups[1].group_id]
    original.service_ids = [services[0].service_id, services[1].service_id]
    dbsession.commit()

    response = client.post(f"{URL}/{original.id}/restore")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["removed_group_ids"] == []
    assert response.json()["removed_service_ids"] == []
    restored = fresh_note(dbsession, original.id)
    assert restored.group_ids == [groups[0].group_id, groups[1].group_id]
    assert restored.service_ids == [services[0].service_id, services[1].service_id]


def test_restore_without_end_ts(client, dbsession, mock_datetime_now, notes):
    original = notes[3]
    original.is_always = False
    original.end_ts = None
    dbsession.commit()

    response = client.post(f"{URL}/{original.id}/restore")
    assert response.status_code == status.HTTP_200_OK
    assert fresh_note(dbsession, original.id).status == ModalStatus.ACTIVE


def test_archive_restore_round_trip(client, dbsession, mock_datetime_now, notes):
    id = notes[0].id
    assert client.post(f"{URL}/{id}/archive").status_code == status.HTTP_200_OK
    assert client.post(f"{URL}/{id}/archive").status_code == status.HTTP_409_CONFLICT
    assert client.post(f"{URL}/{id}/restore").status_code == status.HTTP_200_OK
    assert client.post(f"{URL}/{id}/restore").status_code == status.HTTP_409_CONFLICT
    assert fresh_note(dbsession, id).status == ModalStatus.ACTIVE


def test_old_patch_endpoint_is_removed(client, notes):
    response = client.patch(f"{URL}/{notes[0].id}/status")
    assert response.status_code == status.HTTP_404_NOT_FOUND
