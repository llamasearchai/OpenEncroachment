from __future__ import annotations

import json
import os
import pathlib
from typing import Any

import requests
import yaml

from open_encroachment.utils.io import (
    ensure_dir,
    hmac_sign,
    load_or_create_hmac_key,
    now_iso,
    write_json,
)


class Dispatcher:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.dispatch = self._merge_dispatch_config(config)
        self.mode = self.dispatch.get("mode", "local")
        self.outbox = self.dispatch.get("outbox_dir", "outbox")
        ensure_dir(self.outbox)
        self.key_path = os.path.join(".secrets", "signing.key")
        self.key = load_or_create_hmac_key(self.key_path)

    def _merge_dispatch_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Merge inline dispatch config with optional YAML at config/dispatcher.yaml.
        - Inline config takes precedence over file-based values.
        - YAML format supports:
            mode: local|webhook
            outbox_dir: path (optional)
            webhook: { url, timeout, ca_bundle, client_cert, client_key, headers }
        """
        base = {
            "mode": "local",
            "outbox_dir": "outbox",
            "headers": {},
        }
        inline = dict(config.get("dispatch", {}))
        # Load file if present
        path = config.get("dispatch_config_path", "config/dispatcher.yaml")
        try:
            p = pathlib.Path(path)
            if p.exists():
                with p.open("r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                if isinstance(data, dict):
                    if "mode" in data:
                        base["mode"] = data["mode"]
                    if "outbox_dir" in data:
                        base["outbox_dir"] = data["outbox_dir"]
                    # Accept retries at top-level for backward compatibility
                    if "retries" in data and data["retries"] is not None:
                        base["retries"] = int(data["retries"])
                    wh = data.get("webhook", {}) or {}
                    if isinstance(wh, dict):
                        if "url" in wh:
                            base["webhook_url"] = wh["url"]
                        for k in (
                            "timeout",
                            "ca_bundle",
                            "client_cert",
                            "client_key",
                            "headers",
                            "retries",
                        ):
                            if k in wh and wh[k] is not None:
                                base[k] = wh[k]
        except Exception:
            # On error reading YAML, just use inline/base
            pass
        # Inline overrides
        base.update(inline)
        return base

    def _package(self, incident: dict[str, Any]) -> dict[str, Any]:
        """Build a dispatch envelope aligned to schemas/envelope.schema.json.
        Fields: id, timestamp, type, destination, payload, signature
        """
        eid = incident.get("id") or "unknown"
        ts = incident.get("timestamp") or now_iso()
        destination = (
            incident.get("location", {}).get("geofence_id")
            if isinstance(incident.get("location"), dict)
            else incident.get("geofence_id")
        ) or "unknown"
        payload = {
            "severity": incident.get("severity", {}).get("overall"),
            "threat_probability": incident.get("threat_probability"),
            "location": (
                incident.get("location")
                if isinstance(incident.get("location"), dict)
                else {
                    "lat": incident.get("lat"),
                    "lon": incident.get("lon"),
                    "geofence_id": incident.get("geofence_id"),
                }
            ),
            "sources": incident.get("sources", []),
        }
        body = json.dumps(
            {
                "id": eid,
                "timestamp": ts,
                "type": "incident.notice",
                "destination": destination,
                "payload": payload,
            },
            separators=(",", ":"),
        ).encode("utf-8")
        sig = hmac_sign(self.key, body)
        envelope = {
            "id": eid,
            "timestamp": ts,
            "type": "incident.notice",
            "destination": destination,
            "payload": payload,
            "signature": sig,
        }
        return envelope

    def notify(self, incident: dict[str, Any]) -> None:
        envelope = self._package(incident)
        # Always write to outbox
        out_path = pathlib.Path(self.outbox) / f"notice_{incident['id']}.json"
        write_json(out_path, envelope)
        if self.mode == "webhook":
            url = self.dispatch.get("webhook_url")
            headers = self.dispatch.get("headers", {})
            if url:
                from contextlib import suppress

                # Optional schema validation + httpx sending; fallback to requests
                with suppress(Exception):
                    import json

                    from .webhook import HTTPSDispatcher  # lazy import to avoid hard dependency

                    schema_path = pathlib.Path("schemas/envelope.schema.json")
                    envelope_schema = (
                        json.loads(schema_path.read_text(encoding="utf-8"))
                        if schema_path.exists()
                        else {"type": "object"}
                    )
                    https = HTTPSDispatcher(
                        url=url,
                        envelope_schema=envelope_schema,
                        timeout=float(self.dispatch.get("timeout", 10.0)),
                        ca_bundle=self.dispatch.get("ca_bundle"),
                        client_cert=self.dispatch.get("client_cert"),
                        client_key=self.dispatch.get("client_key"),
                        retries=int(self.dispatch.get("retries", 5)),
                    )
                    https.validate_envelope(envelope)
                    https.send(envelope)

                # Best-effort legacy POST using requests
                with suppress(Exception):
                    requests.post(url, json=envelope, headers=headers, timeout=10)
