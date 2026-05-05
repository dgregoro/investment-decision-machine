from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.core import database as database_module
from app.core.config import clear_settings_cache
from app.main import app


@pytest.fixture(autouse=True)
def _isolated_sqlite(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    database_module.reset_engine_registry()
    clear_settings_cache()
    yield
    database_module.reset_engine_registry()
    clear_settings_cache()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
