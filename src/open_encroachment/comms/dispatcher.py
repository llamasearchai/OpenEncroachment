from __future__ import annotations

import json
import os
import pathlib
from typing import Any

import requests

from ..utils.io import ensure_dir, hmac_sign, load_or_create_hmac_key, now_iso, write_json


class Dispatcher:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.mode = config.get("dispatch", {}).get("mode", "local")
        self.outbox = config.get("dispatch", {}).get("outbox_dir", "outbox")
        ensure_dir(self.outbox)
        self.key_path = os.path.join(".secrets", "signing.key")
        self.key = load_or_create_hmac_key(self.key_path)

    def _package(self, incident: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "schema": "openencroachment.notice.v1",
            "issued_at": now_iso(),
            "incident": incident,
        }
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        sig = hmac_sign(self.key, body)
        envelope = {
            "payload": payload,
            "signature": sig,
            "alg": "HMAC-SHA256",
            "kid": "default",
        }
        return envelope

    def notify(self, incident: dict[str, Any]) -> None:
        envelope = self._package(incident)
        # Always write to outbox
        out_path = pathlib.Path(self.outbox) / f"notice_{incident['id']}.json"
        write_json(out_path, envelope)
        if self.mode == "webhook":
            url = self.config.get("dispatch", {}).get("webhook_url")
            headers = self.config.get("dispatch", {}).get("headers", {})
            if url:
                try:
                    requests.post(url, json=envelope, headers=headers, timeout=10)
                except Exception:
                    # Fall back to local only
                    pass

