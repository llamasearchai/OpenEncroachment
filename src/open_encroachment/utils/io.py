from __future__ import annotations

import base64
import hashlib
import hmac
import os
import pathlib
from typing import Any


def ensure_dir(path: str | os.PathLike) -> None:
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def gen_id(prefix: str = "evt") -> str:
    import uuid

    return f"{prefix}_{uuid.uuid4().hex}"


def write_json(path: str | os.PathLike, data: Any) -> None:
    import json

    p = pathlib.Path(path)
    if p.parent:
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def append_jsonl(path: str | os.PathLike, data: Any) -> None:
    import json

    p = pathlib.Path(path)
    if p.parent:
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, separators=(",", ":")) + "\n")


def read_json(path: str | os.PathLike) -> Any:
    import json

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def file_sha256(path: str | os.PathLike) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_or_create_hmac_key(key_path: str | os.PathLike) -> bytes:
    p = pathlib.Path(key_path)
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        key = os.urandom(32)
        with p.open("wb") as f:
            f.write(key)
        return key
    return p.read_bytes()


def hmac_sign(key: bytes, data: bytes) -> str:
    mac = hmac.new(key, data, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode("ascii")

