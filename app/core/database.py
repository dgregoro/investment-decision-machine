from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def reset_engine_registry() -> None:
    """Drop cached connections (primarily for tests or settings changes)."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None


def _sqlite_connect_kwargs(url: str) -> tuple[dict[str, Any], dict[str, Any]]:
    kwargs: dict[str, Any] = {}
    connect_args: dict[str, Any] = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if ":memory:" in url:
            kwargs["poolclass"] = StaticPool
    return kwargs, connect_args


def configure_engine(database_url: str | None = None) -> Engine:
    global _engine, _session_factory
    url = database_url if database_url is not None else get_settings().database_url
    engine_kwargs, connect_args = _sqlite_connect_kwargs(url)
    _engine = create_engine(url, connect_args=connect_args, **engine_kwargs)
    _session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    return _engine


def get_engine() -> Engine:
    if _engine is None:
        configure_engine()
    assert _engine is not None
    return _engine


def init_db(database_url: str | None = None) -> None:
    """Ensure engine exists and SQLite tables reflect current models."""

    from app.models import Base  # noqa: PLC0415 — defer import until metadata is needed

    if database_url is not None:
        reset_engine_registry()
        configure_engine(database_url)
    elif _engine is None:
        configure_engine()

    bind = get_engine()
    Base.metadata.create_all(bind=bind)


def get_session_factory() -> sessionmaker[Session]:
    if _session_factory is None:
        configure_engine()
    assert _session_factory is not None
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
