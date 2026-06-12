from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import func, select

from ai_world_cup.data.ingest import ingest_source_payload
from ai_world_cup.data.snapshots import write_snapshot
from ai_world_cup.data_sources.api_football import APIFootballSource
from ai_world_cup.data_sources.base import DataSourceError
from ai_world_cup.data_sources.football_data_org import FootballDataOrgSource
from ai_world_cup.data_sources.openfootball import OpenFootballSource
from ai_world_cup.data_sources.worldcup26 import WorldCup26Source
from ai_world_cup.db import get_session, init_db
from ai_world_cup.evaluation.leaderboard import build_leaderboard
from ai_world_cup.evaluation.metrics import score_prediction
from ai_world_cup.evaluation.tournament import build_tournament_leaderboard
from ai_world_cup.prompts.prompt_exporter import (
    create_match_prompt,
    create_tournament_prompt,
    export_prompts,
)
from ai_world_cup.readme_export import update_readme_leaderboard
from ai_world_cup.responses.importer import import_manual_response
from ai_world_cup.responses.tournament_importer import (
    import_tournament_response,
    revalidate_tournament_response,
)
from ai_world_cup.schemas import (
    DataSnapshot,
    EvaluationResult,
    GeneratedPrompt,
    LLMModel,
    ManualResponse,
    Match,
    Prediction,
    Team,
    TournamentManualResponse,
    TournamentPrediction,
    TournamentPromptRun,
)
from ai_world_cup.site_export import export_site_data

app = typer.Typer(help="AI World Cup offline LLM prediction benchmark.")
data_app = typer.Typer(help="Sync and inspect football data.")
prompts_app = typer.Typer(help="Generate and export standardized prompts.")
responses_app = typer.Typer(help="Import manual LLM responses.")
evaluate_app = typer.Typer(help="Evaluate predictions.")
leaderboard_app = typer.Typer(help="Show leaderboards.")
site_app = typer.Typer(help="Export static website data.")
readme_app = typer.Typer(help="Update README generated sections.")
app.add_typer(data_app, name="data")
app.add_typer(prompts_app, name="prompts")
app.add_typer(responses_app, name="responses")
app.add_typer(evaluate_app, name="evaluate")
app.add_typer(leaderboard_app, name="leaderboard")
app.add_typer(site_app, name="site")
app.add_typer(readme_app, name="readme")
console = Console()


def _source_for(name: str):
    normalized = name.strip().lower()
    if normalized == "openfootball":
        return OpenFootballSource()
    if normalized == "worldcup26":
        return WorldCup26Source()
    if normalized in {"football_data_org", "football-data.org", "football-data"}:
        return FootballDataOrgSource()
    if normalized in {"api_football", "api-football"}:
        return APIFootballSource()
    raise typer.BadParameter(f"Unknown source: {name}")


@data_app.command("sync")
def sync_data(
    sources: Annotated[str, typer.Option(help="Comma-separated source names.")] = "openfootball",
) -> None:
    """Fetch football data, save snapshots, and normalize supported sources."""
    init_db()
    with get_session() as session:
        table = Table("source", "snapshot", "teams", "stadiums", "matches", "status")
        for source_name in [item.strip() for item in sources.split(",") if item.strip()]:
            source = _source_for(source_name)
            try:
                payload = source.fetch()
                snapshot = write_snapshot(session, source.name, payload, description="CLI sync")
                counts = ingest_source_payload(session, source.name, payload, snapshot)
                status = payload.get("skipped") or "ok"
                table.add_row(
                    source.name,
                    str(snapshot.id),
                    str(counts["teams"]),
                    str(counts["stadiums"]),
                    str(counts["matches"]),
                    status,
                )
            except DataSourceError as exc:
                table.add_row(source.name, "-", "0", "0", "0", f"failed: {exc}")
        console.print(table)


@data_app.command("status")
def data_status() -> None:
    """Show local database counts."""
    init_db()
    with get_session() as session:
        table = Table("entity", "count")
        for label, model in [
            ("teams", Team),
            ("matches", Match),
            ("data_snapshots", DataSnapshot),
            ("generated_prompts", GeneratedPrompt),
            ("manual_responses", ManualResponse),
            ("predictions", Prediction),
            ("tournament_prompt_runs", TournamentPromptRun),
            ("tournament_manual_responses", TournamentManualResponse),
            ("tournament_predictions", TournamentPrediction),
        ]:
            count = session.exec(select(func.count()).select_from(model)).one()
            table.add_row(label, str(count))
        console.print(table)


@prompts_app.command("generate-match")
def generate_match(match_id: int, version: str = "v1") -> None:
    """Generate one standardized match prompt."""
    init_db()
    with get_session() as session:
        prompt = create_match_prompt(session, match_id, version)
        console.print(f"Generated prompt {prompt.id}: {prompt.prompt_file_path}")


@prompts_app.command("generate-upcoming")
def generate_upcoming(limit: int = 10, version: str = "v1") -> None:
    """Generate prompts for upcoming matches."""
    init_db()
    with get_session() as session:
        matches = list(
            session.exec(
                select(Match)
                .where(Match.home_score.is_(None), Match.away_score.is_(None))
                .order_by(Match.kickoff_utc)
                .limit(limit)
            )
        )
        for match in matches:
            prompt = create_match_prompt(session, match.id, version)
            console.print(f"Generated prompt {prompt.id}: {prompt.prompt_file_path}")


@prompts_app.command("generate-tournament")
def generate_tournament(version: str = "v1") -> None:
    """Generate one full-tournament prompt and JSON context file."""
    init_db()
    with get_session() as session:
        prompt = create_tournament_prompt(session, version)
        json_path = prompt.prompt_file_path.replace(".md", ".json")
        console.print(f"Generated tournament prompt {prompt.id}: {prompt.prompt_file_path}")
        console.print(f"Generated tournament context: {json_path}")


@prompts_app.command("export")
def prompts_export(format: str = "markdown") -> None:
    """Export generated prompts as markdown or JSON."""
    init_db()
    with get_session() as session:
        prompts = list(session.exec(select(GeneratedPrompt).order_by(GeneratedPrompt.id)))
        path = export_prompts(prompts, format)
        console.print(f"Exported {len(prompts)} prompts to {path}")


@prompts_app.command("list")
def prompts_list() -> None:
    """Show generated prompt file paths."""
    init_db()
    with get_session() as session:
        table = Table("type", "id", "match_id", "version", "path")
        for prompt in session.exec(select(GeneratedPrompt).order_by(GeneratedPrompt.id)):
            table.add_row(
                "match",
                str(prompt.id),
                str(prompt.match_id),
                prompt.prompt_version,
                prompt.prompt_file_path,
            )
        for prompt in session.exec(select(TournamentPromptRun).order_by(TournamentPromptRun.id)):
            table.add_row(
                "tournament",
                str(prompt.id),
                "",
                prompt.prompt_version,
                prompt.prompt_file_path,
            )
        console.print(table)


@responses_app.command("import")
def responses_import(
    prompt_id: Annotated[int, typer.Option(help="Generated prompt ID.")],
    model_name: Annotated[str, typer.Option(help="Model display name.")],
    provider: Annotated[str, typer.Option(help="Provider name.")],
    response_file: Annotated[Path, typer.Option(help="Path to raw response file.")],
    model_version: Annotated[str | None, typer.Option(help="Optional model version/date.")] = None,
) -> None:
    """Import a manually saved LLM response file."""
    init_db()
    with get_session() as session:
        manual = import_manual_response(
            session=session,
            prompt_id=prompt_id,
            model_name=model_name,
            provider=provider,
            response_file=response_file,
            model_version=model_version,
        )
        console.print(
            f"Imported response {manual.id} with status {manual.parse_status}: "
            f"{manual.validation_errors_json}"
        )


@responses_app.command("import-tournament")
def responses_import_tournament(
    prompt_id: Annotated[int, typer.Option(help="Tournament prompt run ID.")],
    model_name: Annotated[str, typer.Option(help="Model display name.")],
    provider: Annotated[str, typer.Option(help="Provider name.")],
    response_file: Annotated[Path, typer.Option(help="Path to raw tournament response file.")],
    model_version: Annotated[str | None, typer.Option(help="Optional model version/date.")] = None,
) -> None:
    """Import a manually saved full-tournament LLM response file."""
    init_db()
    with get_session() as session:
        manual = import_tournament_response(
            session=session,
            prompt_id=prompt_id,
            model_name=model_name,
            provider=provider,
            response_file=response_file,
            model_version=model_version,
        )
        console.print(
            f"Imported tournament response {manual.id} with status {manual.parse_status}: "
            f"{manual.validation_errors_json}"
        )


@responses_app.command("validate-tournament")
def responses_validate_tournament(
    response_id: Annotated[int, typer.Option(help="Tournament manual response ID.")],
) -> None:
    """Revalidate a stored full-tournament response."""
    init_db()
    with get_session() as session:
        manual = revalidate_tournament_response(session, response_id)
        console.print(
            f"Validated tournament response {manual.id} with status {manual.parse_status}: "
            f"{manual.validation_errors_json}"
        )


@evaluate_app.command("matches")
def evaluate_matches(completed_only: bool = True) -> None:
    """Evaluate match-by-match predictions against completed match scores."""
    init_db()
    with get_session() as session:
        predictions = list(session.exec(select(Prediction)))
        evaluated = 0
        for prediction in predictions:
            match = session.get(Match, prediction.match_id)
            if not match:
                continue
            if completed_only and (match.home_score is None or match.away_score is None):
                continue
            breakdown = score_prediction(prediction, match)
            existing = session.exec(
                select(EvaluationResult).where(
                    EvaluationResult.model_id == prediction.model_id,
                    EvaluationResult.match_id == prediction.match_id,
                )
            ).first()
            result = existing or EvaluationResult(
                model_id=prediction.model_id,
                match_id=prediction.match_id,
            )
            result.exact_score_points = breakdown.exact_score_points
            result.outcome_points = breakdown.outcome_points
            result.winner_points = breakdown.winner_points
            result.goal_diff_points = breakdown.goal_diff_points
            result.total_points = breakdown.total_points
            session.add(result)
            evaluated += 1
        session.commit()
        console.print(f"Evaluated {evaluated} predictions")


@evaluate_app.command("tournament")
def evaluate_tournament(completed_only: bool = True) -> None:
    """Evaluate full-tournament predictions gradually as results arrive."""
    init_db()
    with get_session() as session:
        rows = build_tournament_leaderboard(session, completed_only=completed_only)
        console.print(f"Evaluated {len(rows)} tournament model submissions")


@leaderboard_app.command("matches")
def leaderboard_matches() -> None:
    """Show match-by-match model leaderboard."""
    init_db()
    with get_session() as session:
        table = Table(
            "rank",
            "model name",
            "provider",
            "matches predicted",
            "total points",
            "average points",
            "outcome accuracy",
            "exact score accuracy",
            "average confidence",
        )
        for row in build_leaderboard(session):
            table.add_row(
                str(row.rank),
                row.model_name,
                row.provider,
                str(row.matches_predicted),
                str(row.total_points),
                f"{row.average_points:.2f}",
                f"{row.outcome_accuracy:.2%}",
                f"{row.exact_score_accuracy:.2%}",
                f"{row.average_confidence:.2f}",
            )
        console.print(table)


@leaderboard_app.command("tournament")
def leaderboard_tournament(completed_only: bool = True) -> None:
    """Show full-tournament model leaderboard."""
    init_db()
    with get_session() as session:
        table = Table(
            "rank",
            "model name",
            "provider",
            "total tournament points",
            "group-stage points",
            "group-standing points",
            "knockout points",
            "champion prediction",
            "exact score accuracy",
            "outcome accuracy",
            "average confidence",
        )
        for rank, row in enumerate(
            build_tournament_leaderboard(session, completed_only=completed_only),
            start=1,
        ):
            table.add_row(
                str(rank),
                row.model_name,
                row.provider,
                str(row.total_tournament_points),
                str(row.group_stage_points),
                str(row.group_standing_points),
                str(row.knockout_points),
                row.champion_prediction,
                f"{row.exact_score_accuracy:.2%}",
                f"{row.outcome_accuracy:.2%}",
                f"{row.average_confidence:.2f}",
            )
        console.print(table)


@site_app.command("export")
def site_export(
    output_dir: Annotated[
        Path | None,
        typer.Option(help="Output directory for website JSON files."),
    ] = None,
) -> None:
    """Export static JSON files consumed by the GitHub Pages website."""
    init_db()
    with get_session() as session:
        written = export_site_data(session, output_dir)
        for path in written:
            console.print(f"Wrote {path}")


@readme_app.command("leaderboard")
def readme_leaderboard(
    readme_path: Annotated[
        Path,
        typer.Option(help="README path to update."),
    ] = Path("README.md"),
    limit: Annotated[int, typer.Option(help="Maximum models to show.")] = 10,
    completed_only: Annotated[
        bool,
        typer.Option(help="Only evaluate predictions for matches with actual scores."),
    ] = True,
) -> None:
    """Update the generated tournament leaderboard table in README.md."""
    init_db()
    with get_session() as session:
        path = update_readme_leaderboard(
            session,
            readme_path=readme_path,
            limit=limit,
            completed_only=completed_only,
        )
        console.print(f"Updated README leaderboard: {path}")


@app.command("dashboard")
def dashboard() -> None:
    """Launch the optional Streamlit dashboard."""
    import subprocess

    app_path = Path(__file__).parent / "dashboard" / "streamlit_app.py"
    raise typer.Exit(subprocess.call(["streamlit", "run", str(app_path)]))


@app.command("models")
def models() -> None:
    """List registered manual models."""
    init_db()
    with get_session() as session:
        table = Table("id", "model", "provider", "version", "access")
        for model in session.exec(select(LLMModel).order_by(LLMModel.id)):
            table.add_row(
                str(model.id),
                model.model_display_name,
                model.provider,
                model.model_version or "",
                model.access_mode,
            )
        console.print(table)


if __name__ == "__main__":
    app()
