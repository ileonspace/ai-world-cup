from __future__ import annotations

import json
from pathlib import Path

from sqlmodel import Session

from ai_world_cup.config import get_settings
from ai_world_cup.prompts.prompt_builder import build_match_prompt
from ai_world_cup.prompts.tournament_prompt_builder import build_tournament_prompt
from ai_world_cup.schemas import GeneratedPrompt, Match, PromptRun, TournamentPromptRun


def create_match_prompt(session: Session, match_id: int, version: str = "v1") -> GeneratedPrompt:
    prompt_text = build_match_prompt(session, match_id, version)
    match = session.get(Match, match_id)
    if not match:
        raise ValueError(f"No match found with id {match_id}")
    run = PromptRun(
        prompt_version=version,
        prompt_type="match",
        data_snapshot_id=match.data_snapshot_id,
        notes=f"Generated for match {match_id}",
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    output_dir = get_settings().resolve_path("data/prompts/match")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"match_{match_id:03d}_{version}_prompt.md"
    path.write_text(prompt_text, encoding="utf-8")
    generated = GeneratedPrompt(
        prompt_run_id=run.id,
        match_id=match_id,
        prompt_type="match",
        prompt_version=version,
        prompt_text=prompt_text,
        prompt_file_path=str(Path("data/prompts/match") / path.name),
    )
    session.add(generated)
    session.commit()
    session.refresh(generated)
    return generated


def export_prompts(prompts: list[GeneratedPrompt], output_format: str) -> Path:
    output_dir = get_settings().resolve_path("data/exports")
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_format == "json":
        path = output_dir / "generated_prompts.json"
        path.write_text(
            json.dumps([prompt.model_dump(mode="json") for prompt in prompts], indent=2),
            encoding="utf-8",
        )
        return path
    if output_format == "markdown":
        path = output_dir / "generated_prompts.md"
        body = "\n\n---\n\n".join(prompt.prompt_text for prompt in prompts)
        path.write_text(body, encoding="utf-8")
        return path
    raise ValueError("format must be markdown or json")


def create_tournament_prompt(session: Session, version: str = "v1") -> TournamentPromptRun:
    prompt_text, context = build_tournament_prompt(session, version)
    run = TournamentPromptRun(
        prompt_version=version,
        data_snapshot_id=context["data_snapshot_id"],
        prompt_file_path="",
        notes="Full-tournament prompt",
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    output_dir = get_settings().resolve_path("data/prompts/tournament")
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"tournament_prediction_{version}_{run.id}.md"
    json_path = output_dir / f"tournament_prediction_{version}_{run.id}.json"
    md_path.write_text(prompt_text, encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "prompt_run_id": run.id,
                "prompt_version": version,
                "data_snapshot_id": context["data_snapshot_id"],
                "prompt_text": prompt_text,
                "context": context,
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    run.prompt_file_path = str(Path("data/prompts/tournament") / md_path.name)
    session.add(run)
    session.commit()
    session.refresh(run)
    return run
