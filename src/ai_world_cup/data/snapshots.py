from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from sqlmodel import Session

from ai_world_cup.config import get_settings
from ai_world_cup.schemas import DataSnapshot


def write_snapshot(
    session: Session,
    source_name: str,
    payload: dict[str, Any],
    description: str | None = None,
) -> DataSnapshot:
    settings = get_settings()
    encoded = json.dumps(payload, sort_keys=True, default=str, indent=2)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    snapshots_dir = settings.resolve_path("data/snapshots")
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    path = snapshots_dir / f"{source_name}_{digest[:12]}.json"
    path.write_text(encoded, encoding="utf-8")
    snapshot = DataSnapshot(
        source_name=source_name,
        snapshot_hash=digest,
        raw_file_path=str(Path("data/snapshots") / path.name),
        description=description,
    )
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    return snapshot
