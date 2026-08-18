from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from modal_backend.models.db import Group, ModalStatus, Note, NoteTypeEnum, Service
from modal_backend.schemas.models import (
    NoteChoicePost,
    NoteImagePost,
    NoteInfoPost,
    NoteRatingPost,
    NoteTextPost,
)
from modal_backend.settings import Settings

NOW = datetime.now(timezone.utc).replace(tzinfo=None)


class PostgresConfig:
    """Дата-класс со значениями для контейнера с тестовой БД и для alembic-миграции."""

    container_name: str = "modal_backend-test"
    username: str = "postgres"
    host: str = "localhost"
    external_port: int = 5433
    image: str = "postgres:15"
    host_auth_method: str = "trust"
    alembic_ini: str = Path(__file__).resolve().parent.parent / "alembic.ini"

    @classmethod
    def get_url(cls) -> str:
        """Возвращает URI для подключения к БД."""
        return f"postgresql://{cls.username}@{cls.host}:{cls.external_port}/postgres"


@pytest.fixture(scope="session")
def session_mp():
    mp = MonkeyPatch()
    yield mp
    mp.undo()


@pytest.fixture(scope="session")
def get_settings_mock(session_mp):
    """Переопределение get_settings в modal_backend/settings.py."""

    @lru_cache
    def get_test_settings():
        test_settings = Settings()
        test_settings.DB_DSN = PostgresConfig.get_url()
        return test_settings

    dsn_mock = session_mp.setattr("modal_backend.settings.get_settings", get_test_settings)
    return dsn_mock


@pytest.fixture(scope="session")
def get_app_with_test_settings(get_settings_mock):
    """Загрузка app с тестовыми настройками."""
    from modal_backend.routes import app

    return app


@pytest.fixture(scope="session")
def db_container(get_settings_mock):
    """Фикстура настройки БД для тестов в Docker-контейнере."""
    container = (
        PostgresContainer(
            image=PostgresConfig.image, username=PostgresConfig.username, dbname=PostgresConfig.container_name
        )
        .with_bind_ports(5432, PostgresConfig.external_port)
        .with_env("POSTGRES_HOST_AUTH_METHOD", PostgresConfig.host_auth_method)
        .with_name(PostgresConfig.container_name)
    )
    container.start()
    alembic_ini = PostgresConfig.alembic_ini
    cfg = AlembicConfig(str(alembic_ini.resolve()))
    cfg.set_main_option("script_location", "%(here)s/migrations")
    command.upgrade(cfg, "head")
    try:
        yield PostgresConfig.get_url()
    finally:
        container.stop()


@pytest.fixture(scope="session")
def engine(db_container):
    """Фикстура настройки пула соединений к БД."""
    engine = create_engine(str(db_container), pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture()
def dbsession(engine):
    """Фикстура настройки Session для работы с БД в тестах."""
    TestingLocalSession = sessionmaker(bind=engine)
    session = TestingLocalSession()
    yield session
    session.close()


@pytest.fixture()
def authlib_user_data():
    """
    Данные о пользователе, возвращаемые сервисом auth.
    """
    return {
        "session_scopes": [{"id": 0, "name": "string", "comment": "string"}],
        "user_scopes": [{"id": 0, "name": "string", "comment": "string"}],
        "indirect_groups": [{"id": 0, "name": "string", "parent_id": 0}],
        "groups": [{"id": 0, "name": "string", "parent_id": 0}],
        "id": 0,
        "email": "string",
        "userdata": [
            {"category": "Личная информация", "param": "Полное имя", "value": "Тестовый Тест"},
        ],
    }


@pytest.fixture()
def authlib_mock(mocker):
    auth_mock = mocker.patch("auth_lib.fastapi.UnionAuth.__call__", autospec=True)
    return auth_mock


@pytest.fixture()
def user_mock(authlib_mock, authlib_user_data):
    authlib_mock.return_value = authlib_user_data
    return authlib_mock


@pytest.fixture()
def client(get_app_with_test_settings, user_mock):
    app = get_app_with_test_settings
    client = TestClient(app)
    return client


def create_group(group_id: int, name: str) -> Group:
    """Вспомогательная функция-мини-фабрика для создания разных групп в фикстуре groups."""
    return Group(group_id=group_id, name=name)


@pytest.fixture()
def groups(dbsession):
    """Создает три группы."""
    group_data = [(1, "Group_1"), (2, "Group_2"), (3, "Group_3")]
    groups = [create_group(*group) for group in group_data]
    for group in groups:
        dbsession.add(group)
    dbsession.commit()
    yield groups
    for group in groups:
        dbsession.delete(group)
    dbsession.commit()


def create_service(service_id: int, name: str) -> Service:
    """Вспомогательная функция-мини-фабрика для создания разных сервисов в фикстуре services."""
    return Service(service_id=service_id, name=name)


@pytest.fixture()
def services(dbsession):
    """Создает три сервиса."""
    service_data = [(1, "Service_1"), (2, "Service_2"), (3, "Service_3")]
    services = [create_service(*service) for service in service_data]
    for service in services:
        dbsession.add(service)
    dbsession.commit()
    yield services
    for service in services:
        dbsession.delete(service)
    dbsession.commit()


@pytest.fixture()
def mock_datetime_now(mocker):
    mock_datetime = mocker.patch("modal_backend.utils.services.datetime")
    mock_datetime.now.return_value = NOW
    yield


def create_note(
    type_id: int,
    schema: NoteChoicePost | NoteImagePost | NoteInfoPost | NoteRatingPost | NoteTextPost,
    admin_id: int,
    status: ModalStatus,
):
    return Note(
        type_id=type_id,
        **schema.model_dump(),
        admin_id=admin_id,
        status=status,
    )


@pytest.fixture()
def notes(
    dbsession,
    groups,
    services,
    authlib_user_data,
):
    """Создает 8 модалок:
    indexes:         descriprion:
    (0, 1, 2, 3, 4)  5 с разными типами
    (0, 1, 2)        3 активные
    (3, 4, 5, 6, 7)  5 архивных
    (0, 2, 4, 6, 7)  group_ids = [3] service_ids = [3]
    (1, 3)           group_ids = [1, 2] service_ids = [1, 2]
    (5)              group_ids - [1, 2, 3] service_ids = [1, 2, 3]
    (6, 7)           просроченные, одна с is_always=True
    """
    note_data = [
        {
            "type_id": NoteTypeEnum.INFO,
            "schema": NoteInfoPost(
                header="header_1",
                is_always=False,
                frequency=10,
                group_ids=[group.id for group in groups][2:3],
                service_ids=[service.id for service in services][2:3],
            ),
            "admin_id": authlib_user_data.get("id"),
            "status": ModalStatus.ACTIVE,
        },
        {
            "type_id": NoteTypeEnum.RATING,
            "schema": NoteRatingPost(
                header="header_2",
                is_always=False,
                frequency=10,
                group_ids=[group.id for group in groups][:2],
                service_ids=[service.id for service in services][:2],
            ),
            "admin_id": authlib_user_data.get("id"),
            "status": ModalStatus.ACTIVE,
        },
        {
            "type_id": NoteTypeEnum.TEXT,
            "schema": NoteTextPost(
                header="header_3",
                is_always=False,
                frequency=10,
                group_ids=[group.id for group in groups][2:3],
                service_ids=[service.id for service in services][2:3],
            ),
            "admin_id": authlib_user_data.get("id"),
            "status": ModalStatus.ACTIVE,
        },
        {
            "type_id": NoteTypeEnum.CHOICE,
            "schema": NoteChoicePost(
                header="header_4",
                is_always=False,
                frequency=10,
                group_ids=[group.id for group in groups][:2],
                service_ids=[service.id for service in services][:2],
            ),
            "admin_id": authlib_user_data.get("id"),
            "status": ModalStatus.ARCHIVED,
        },
        {
            "type_id": NoteTypeEnum.IMAGE,
            "schema": NoteImagePost(
                header="header_5",
                is_always=False,
                frequency=10,
                group_ids=[group.id for group in groups][2:3],
                service_ids=[service.id for service in services][2:3],
            ),
            "admin_id": authlib_user_data.get("id"),
            "status": ModalStatus.ARCHIVED,
        },
        {
            "type_id": NoteTypeEnum.IMAGE,
            "schema": NoteImagePost(
                header="header_5",
                is_always=False,
                frequency=10,
                group_ids=[group.id for group in groups],
                service_ids=[service.id for service in services],
            ),
            "admin_id": authlib_user_data.get("id"),
            "status": ModalStatus.ARCHIVED,
        },
    ]

    for offset, d in enumerate(note_data):
        d["schema"].start_ts = NOW + offset * timedelta(hours=1)
        d["schema"].end_ts = NOW + offset * timedelta(hours=1) + timedelta(hours=1)
    note_data.extend(
        [
            {  # просроченная модалка index 6
                "type_id": NoteTypeEnum.IMAGE,
                "schema": NoteImagePost(
                    header="header_6",
                    is_always=False,
                    frequency=10,
                    group_ids=[group.id for group in groups][2:3],
                    service_ids=[service.id for service in services][2:3],
                    start_ts=NOW + timedelta(hours=2) * 5,
                    end_ts=NOW - timedelta(hours=1) * 5,
                ),
                "admin_id": authlib_user_data.get("id"),
                "status": ModalStatus.ARCHIVED,
            },
            {  # просроченная модалка c is_always=True index 7
                "type_id": NoteTypeEnum.IMAGE,
                "schema": NoteImagePost(
                    header="header_7",
                    is_always=True,
                    frequency=10,
                    group_ids=[group.id for group in groups][2:3],
                    service_ids=[service.id for service in services][2:3],
                    start_ts=NOW + timedelta(hours=3) * 5,
                    end_ts=NOW - timedelta(hours=1) * 5,
                ),
                "admin_id": authlib_user_data.get("id"),
                "status": ModalStatus.ARCHIVED,
            },
        ]
    )
    notes = [create_note(**note) for note in note_data]

    for note in notes:
        dbsession.add(note)
    dbsession.commit()
    yield notes
    for note in notes:
        dbsession.delete(note)
    dbsession.commit()
