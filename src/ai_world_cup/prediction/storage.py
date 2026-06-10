from __future__ import annotations

from sqlmodel import Session, select

from ai_world_cup.schemas import Prediction


def predictions_for_model(session: Session, model_id: int) -> list[Prediction]:
    return list(session.exec(select(Prediction).where(Prediction.model_id == model_id)))
