"""Embedded HTTP server utilities for SAPL."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional, Tuple


@dataclass
class SAPLServer:
    """Small HTTP server used for documentation previews and demos."""

    bind: str = "127.0.0.1"
    port: int = 8000
    directory: str = "."

    def __post_init__(self) -> None:
        self._directory = Path(self.directory).resolve()
        handler = partial(SimpleHTTPRequestHandler, directory=str(self._directory))
        self._server = ThreadingHTTPServer((self.bind, self.port), handler, bind_and_activate=False)
        self._server.allow_reuse_address = True
        self._server.server_bind()
        self._server.server_activate()
        self._thread: Optional[threading.Thread] = None
        self._ready = threading.Event()

    @property
    def server_address(self) -> Tuple[str, int]:
        return self._server.server_address  # type: ignore[return-value]

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        def _run() -> None:
            self._ready.set()
            self._server.serve_forever(poll_interval=0.1)

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        self._ready.wait()

    def serve_forever(self) -> None:
        self.start()
        try:
            while True:
                self._server.handle_request()
        except KeyboardInterrupt:  # pragma: no cover - forwarded to caller
            raise

    def handle_once(self) -> None:
        self.start()
        self._server.handle_request()

    def stop(self) -> None:
        if not self._thread:
            return
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)
        self._thread = None

    def __enter__(self) -> "SAPLServer":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()


__all__ = ["SAPLServer"]
