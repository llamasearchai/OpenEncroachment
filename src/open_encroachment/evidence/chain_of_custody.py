from __future__ import annotations

import json
import os
import pathlib
from collections.abc import Iterable
from typing import Any

from ..utils.io import append_jsonl, file_sha256, now_iso


def _ledger_path(config: dict[str, Any]) -> pathlib.Path:
    p = config.get("artifacts", {}).get("evidence_ledger", "artifacts/evidence_ledger.jsonl")
    return pathlib.Path(p)


def append_records(config: dict[str, Any], incident: dict[str, Any], files: Iterable[str]) -> list[dict[str, Any]]:
    ledger = _ledger_path(config)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    prev_hash = "0" * 64
    if ledger.exists():
        # Read last line
        try:
            last = None
            with ledger.open("rb") as f:
                f.seek(0, os.SEEK_END)
                size = f.tell()
                block = 4096
                data = b""
                while size > 0:
                    step = min(block, size)
                    size -= step
                    f.seek(size)
                    chunk = f.read(step)
                    data = chunk + data
                    if b"\n" in data:
                        break
                last_line = data.splitlines()[-1]
                last = json.loads(last_line.decode("utf-8"))
            prev_hash = last.get("chain_hash", prev_hash)
        except Exception:
            pass
    entries: list[dict[str, Any]] = []
    for fp in files:
        fh = file_sha256(fp)
        chain = _sha256_hex(prev_hash + fh)
        entry = {
            "timestamp": now_iso(),
            "incident_id": incident.get("id"),
            "file": fp,
            "file_sha256": fh,
            "prev_hash": prev_hash,
            "chain_hash": chain,
        }
        append_jsonl(ledger, entry)
        entries.append(entry)
        prev_hash = chain
    return entries


def _sha256_hex(s: str) -> str:
    import hashlib

    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def verify_ledger(config: dict[str, Any]) -> tuple[bool, int]:
    """Verify chain-of-custody ledger; returns (ok, checked_count)."""
    ledger = _ledger_path(config)
    if not ledger.exists():
        return True, 0
    prev = "0" * 64
    count = 0
    with ledger.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                return False, count
            expected = _sha256_hex(prev + rec.get("file_sha256", ""))
            if expected != rec.get("chain_hash"):
                return False, count
            prev = rec.get("chain_hash")
            count += 1
    return True, count

