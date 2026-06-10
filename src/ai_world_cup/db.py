from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from ai_world_cup.config import get_settings


def _ensure_sqlite_parent(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return
    db_path = Path(database_url.replace("sqlite:///", "", 1))
    if not db_path.is_absolute():
        db_path = get_settings().project_root / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)


def get_engine(database_url: str | None = None):
    url = database_url or get_settings().database_url
    _ensure_sqlite_parent(url)
    return create_engine(url, echo=False)


def init_db(database_url: str | None = None) -> None:
    engine = get_engine(database_url)
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session(database_url: str | None = None) -> Generator[Session, None, None]:
    engine = get_engine(database_url)
    with Session(engine) as session:
        yield session
