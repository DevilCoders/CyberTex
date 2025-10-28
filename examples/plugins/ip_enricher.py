"""Example SAPL plugin that enriches IP addresses with demo metadata."""

from __future__ import annotations

from datetime import datetime


def register(interpreter):
    """Attach the ``enrich_ip`` helper to the interpreter."""

    def enrich_ip(address: str) -> dict[str, str]:
        return {
            "ip": address,
            "asn": "AS64500",
            "confidence": "high",
            "source": "demo-plugin",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    interpreter.register_builtin("enrich_ip", enrich_ip)
