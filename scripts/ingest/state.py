"""Persistent dedupe state for the ingestion pipeline.

A flat JSON file at ``scripts/ingest/state.json`` records, per source name, the
IDs (URLs, video IDs, entry GUIDs) we've already ingested. ``filter_new()``
takes a list of candidate items and returns only the ones not yet processed.
The file is gitignored — the history lives in commits, not in state.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Sequence

HERE = Path(__file__).resolve().parent
STATE_PATH = HERE / "state.json"


def load() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        with STATE_PATH.open("r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save(state: dict) -> None:
    tmp = STATE_PATH.with_suffix(".json.tmp")
    with tmp.open("w") as f:
        json.dump(state, f, indent=2, sort_keys=True)
    os.replace(tmp, STATE_PATH)


def seen(state: dict, source_name: str) -> set:
    return set(state.get(source_name, {}).get("seen_ids", []))


def record(state: dict, source_name: str, ids: Iterable[str]) -> None:
    entry = state.setdefault(source_name, {})
    bag = set(entry.get("seen_ids", []))
    bag.update(ids)
    # keep last 1000 per source so the file doesn't grow unbounded
    entry["seen_ids"] = sorted(bag)[-1000:]


def filter_new(
    state: dict, source_name: str, items: Sequence[dict], *, id_key: str
) -> list[dict]:
    """Return items whose ``id_key`` value has not been recorded yet."""
    already = seen(state, source_name)
    return [it for it in items if it.get(id_key) and it[id_key] not in already]
