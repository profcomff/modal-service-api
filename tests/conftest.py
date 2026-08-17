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

from modal_backend.settings import Settings


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
