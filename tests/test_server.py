from pathlib import Path
from urllib.request import urlopen

from sapl.server import SAPLServer


def test_sapl_server_serves_files(tmp_path):
    root = Path(tmp_path)
    index = root / "index.html"
    index.write_text("hello sapl", encoding="utf-8")

    server = SAPLServer(bind="127.0.0.1", port=0, directory=str(root))
    with server:
        host, port = server.server_address
        with urlopen(f"http://{host}:{port}/index.html") as response:
            content = response.read().decode("utf-8")
    assert content == "hello sapl"
