from typing import Any

import httpx
from jsonschema import validate
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class HTTPSDispatcher:
    def __init__(
        self,
        url: str,
        envelope_schema: dict[str, Any],
        timeout: float = 10.0,
        ca_bundle: str | None = None,
        client_cert: str | None = None,
        client_key: str | None = None,
    ) -> None:
        self.url = url
        self.envelope_schema = envelope_schema
        self.timeout = timeout
        self._verify = ca_bundle if ca_bundle else True
        self._cert = (client_cert, client_key) if client_cert and client_key else None

    def validate_envelope(self, envelope: dict[str, Any]) -> None:
        validate(instance=envelope, schema=self.envelope_schema)

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=10),
        retry=retry_if_exception_type((httpx.TransportError, httpx.HTTPStatusError)),
    )
    def send(self, envelope: dict[str, Any]) -> httpx.Response:
        self.validate_envelope(envelope)
        with httpx.Client(timeout=self.timeout, verify=self._verify, cert=self._cert) as client:
            resp = client.post(self.url, json=envelope)
            resp.raise_for_status()
            return resp

