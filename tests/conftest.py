# Тут импорты
from functools import lru_cache
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from modal_backend.settings import Settings


class PostgresConfig:
    """Дата-класс со значениями для контейнера с тестовой БД и для alembic-миграции."""

    container_name: str = "modal-service-api_test"
    username: str = "postgres"
    host: str = "localhost"
    external_port: int = 5432
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

    dsn_mock = session_mp.setattr(name="modal_backend.settings.get_settings", value=get_test_settings)
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
        .with_env("POSTGRES_HOST_AUTH_METHOD", PostgresConfig.ham)
        .with_name(PostgresConfig.container_name)
    )
    container.start()
    cfg = AlembicConfig(str(PostgresConfig.alembic_ini.resolve()))
    cfg.set_main_option("script_location", "%(here)s/migrations")
    command.upgrade(cfg, "head")
    try:
        yield PostgresConfig.get_url()
    finally:
        container.stop()


@pytest.fixture(scope="session")
def engine(db_container):
    """Фикстура настройки пула соединений к БД"""
    engine = create_engine(str(db_container), pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture()
def dbsession(engine):
    """Фикстура настройки Session для работы с БД в тестах, реализующая паттерн 'Транзакционный откат'"""
    # берем соединение из пула
    connection = engine.connect()
    # начинаем внешнюю транзакцию(на уровне соедниения)
    transaction = connection.begin()
    # создаём сессю на основе взятого из пула соединения
    session = Session(bind=connection)
    yield session
    # закрываем сессию
    session.close()
    # откатываем внешнюю транзакцию, все savepoint-ы откатываются, БД чиста
    transaction.rollback()
    # возвращаем соединение в пул
    connection.close()


@pytest.fixture
def client(mocker, get_app_with_test_settings):
    app = get_app_with_test_settings
    client = TestClient(app)
    return client
