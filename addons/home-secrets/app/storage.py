import json
import os
from pathlib import Path
from typing import Any

BASE = Path("/data/hs")
BASE.mkdir(parents=True, exist_ok=True)
GOOGLE_FILE = BASE / "google_tokens.json"

def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}

def _write_json(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)

def google_get(label: str) -> dict[str, Any] | None:
    data = _read_json(GOOGLE_FILE)
    return data.get(label)

def google_set(label: str, payload: dict[str, Any]) -> None:
    data = _read_json(GOOGLE_FILE)
    data[label] = payload
    _write_json(GOOGLE_FILE, data)