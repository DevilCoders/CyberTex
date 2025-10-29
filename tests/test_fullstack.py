import json
from pathlib import Path

from sapl.fullstack_preview import preview_fullstack_app, scaffold_fullstack_app
from sapl.stdlib.security_web import Component, FullStackApp, WebAPI


def _build_blueprint() -> FullStackApp:
    app = FullStackApp("test-suite").frontend("reactive-ui").backend("async-api")

    login = Component("LoginWidget").state(username="", password="")
    login.security(rate_limiting="5 attempts per minute", csrf_protection=True)
    app.add_frontend(login)

    api = WebAPI("gateway").middleware(["auth"],).database("encrypted")
    endpoint = api.endpoint("/health", method="GET", authentication="token")
    endpoint.handler("Return operational heartbeat")
    app.add_backend(api)

    return app


def test_scaffold_fullstack_app_writes_bundle(tmp_path):
    app = _build_blueprint()
    bundle = scaffold_fullstack_app(app, tmp_path / "bundle")

    metadata_path = Path(bundle["metadata_path"])
    assert metadata_path.exists()
    metadata = json.loads(metadata_path.read_text())
    assert metadata["name"] == "test-suite"
    assert metadata.get("frontends")

    index_path = Path(bundle["index"])
    assert index_path.exists()
    html = index_path.read_text()
    assert "test-suite" in html


def test_preview_fullstack_app_creates_server(tmp_path):
    app = _build_blueprint()
    result = preview_fullstack_app(app, destination=tmp_path / "preview", port=0)

    server = result["server"]
    bundle = result["bundle"]
    frontend_dir = Path(bundle["frontend_dir"])
    assert frontend_dir.exists()

    host, port = server.server_address
    assert isinstance(host, str)
    assert isinstance(port, int)

    server.stop()
