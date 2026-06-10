from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture()
def session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        yield db
