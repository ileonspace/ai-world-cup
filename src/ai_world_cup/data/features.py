from __future__ import annotations

from sqlmodel import Session, select

from ai_world_cup.schemas import Standing


def standings_for_group(session: Session, group_name: str | None) -> list[Standing]:
    if not group_name:
        return []
    return list(session.exec(select(Standing).where(Standing.group_name == group_name)))
