"""Append-only decision logging for the J.A.R.V.I.S. kernel."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_LOG_PATH = Path(__file__).resolve().parent / "logs" / "decision_log.jsonl"


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    return value


def append_decision_record(record: dict[str, Any], path: str | Path = DEFAULT_LOG_PATH) -> Path:
    log_path = Path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        **{key: _to_jsonable(value) for key, value in record.items()},
    }
    with log_path.open("a", encoding="utf-8") as file:
        json.dump(payload, file, sort_keys=True)
        file.write("\n")
    return log_path

