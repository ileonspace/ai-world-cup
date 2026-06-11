from __future__ import annotations

from pathlib import Path

from sqlmodel import select

from ai_world_cup.db import get_session, init_db
from ai_world_cup.prompts.prompt_exporter import create_tournament_prompt
from ai_world_cup.responses.tournament_importer import import_tournament_response
from ai_world_cup.schemas import TournamentPromptRun
from ai_world_cup.site_export import export_site_data

RESPONSE_IMPORTS = [
    ("Gemini_tournament_v1.json", "Gemini", "Google"),
    ("Mistral_Medium_3_5_tournament_v1.json", "Mistral Medium 3.5", "Mistral"),
    ("GPT_5_5_tournament_v1.json", "GPT-5.5", "OpenAI"),
    ("grok_tournament_v1.json", "Grok", "xAI"),
    ("GPT_5_5_Thinking_tournament_v1.json", "GPT-5.5 Thinking", "OpenAI"),
    ("perplexity_pro_tournament_v1.json", "Perplexity Pro", "Perplexity"),
    ("perplexity_tournament_v1.json", "Perplexity", "Perplexity"),
    ("claude_sonnet_4.6_tournament_v1.json", "Claude Sonnet 4.6", "Anthropic"),
    ("Deepseek_tournament_v1.json", "DeepSeek", "DeepSeek"),
    ("qwen_3_7_tournament_v1.json", "Qwen 3 7", "Qwen"),
]


def main() -> None:
    init_db()
    with get_session() as session:
        prompt = session.exec(
            select(TournamentPromptRun).order_by(TournamentPromptRun.id.desc())
        ).first()
        if prompt is None:
            prompt = create_tournament_prompt(session, "v1")
        for filename, model_name, provider in RESPONSE_IMPORTS:
            response_path = Path("data/responses/manual") / filename
            if response_path.exists():
                manual = import_tournament_response(
                    session=session,
                    prompt_id=prompt.id,
                    model_name=model_name,
                    provider=provider,
                    response_file=response_path,
                )
                print(f"{filename}: {manual.parse_status}")
            else:
                print(f"{filename}: missing, skipped")
        for path in export_site_data(session):
            print(f"wrote {path}")


if __name__ == "__main__":
    main()
