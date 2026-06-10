from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlmodel import select

from ai_world_cup.db import get_session, init_db
from ai_world_cup.evaluation.leaderboard import build_leaderboard
from ai_world_cup.evaluation.tournament import build_tournament_leaderboard
from ai_world_cup.schemas import (
    DataSnapshot,
    GeneratedPrompt,
    ManualResponse,
    Match,
    Prediction,
    TournamentManualResponse,
    TournamentPrediction,
    TournamentPromptRun,
)

st.set_page_config(page_title="AI World Cup", layout="wide")
st.title("AI World Cup")

init_db()


def rows(model):
    with get_session() as session:
        return [item.model_dump() for item in session.exec(select(model))]


sections = [
    "Data overview",
    "Fixtures",
    "Generated prompts",
    "Imported model responses",
    "Tournament responses",
    "Predictions table",
    "Tournament predictions",
    "Match comparison",
    "Leaderboard",
    "Tournament leaderboard",
    "Data snapshot information",
]
section = st.sidebar.radio("Section", sections)

if section == "Data overview":
    st.subheader("Data overview")
    st.dataframe(
        pd.DataFrame(
            [
                {"entity": "fixtures", "count": len(rows(Match))},
                {"entity": "generated prompts", "count": len(rows(GeneratedPrompt))},
                {"entity": "manual responses", "count": len(rows(ManualResponse))},
                {"entity": "predictions", "count": len(rows(Prediction))},
                {"entity": "tournament prompts", "count": len(rows(TournamentPromptRun))},
                {"entity": "tournament responses", "count": len(rows(TournamentManualResponse))},
                {"entity": "tournament predictions", "count": len(rows(TournamentPrediction))},
                {"entity": "snapshots", "count": len(rows(DataSnapshot))},
            ]
        ),
        use_container_width=True,
    )
elif section == "Fixtures":
    st.dataframe(pd.DataFrame(rows(Match)), use_container_width=True)
elif section == "Generated prompts":
    st.dataframe(pd.DataFrame(rows(GeneratedPrompt)), use_container_width=True)
elif section == "Imported model responses":
    st.dataframe(pd.DataFrame(rows(ManualResponse)), use_container_width=True)
elif section == "Tournament responses":
    st.dataframe(pd.DataFrame(rows(TournamentManualResponse)), use_container_width=True)
elif section == "Predictions table":
    st.dataframe(pd.DataFrame(rows(Prediction)), use_container_width=True)
elif section == "Tournament predictions":
    st.dataframe(pd.DataFrame(rows(TournamentPrediction)), use_container_width=True)
elif section == "Match comparison":
    predictions = pd.DataFrame(rows(Prediction))
    if predictions.empty:
        st.info("No predictions imported yet.")
    else:
        match_id = st.selectbox("Match ID", sorted(predictions["match_id"].unique()))
        st.dataframe(predictions[predictions["match_id"] == match_id], use_container_width=True)
elif section == "Leaderboard":
    with get_session() as session:
        st.dataframe(
            pd.DataFrame([row.__dict__ for row in build_leaderboard(session)]),
            use_container_width=True,
        )
elif section == "Tournament leaderboard":
    with get_session() as session:
        st.dataframe(
            pd.DataFrame([row.__dict__ for row in build_tournament_leaderboard(session)]),
            use_container_width=True,
        )
elif section == "Data snapshot information":
    st.dataframe(pd.DataFrame(rows(DataSnapshot)), use_container_width=True)
