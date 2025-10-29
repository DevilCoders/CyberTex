"""Utilities for working with the bundled SAPL advanced website."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict, List

from .server import SAPLServer

WEBSITE_ROOT = Path(__file__).resolve().parent.parent / "website"


def website_root() -> Path:
    """Return the path to the bundled website assets."""

    if not WEBSITE_ROOT.exists():
        raise FileNotFoundError("The SAPL advanced website assets are missing.")
    return WEBSITE_ROOT


def list_website_assets() -> List[str]:
    """Return a sorted list of relative file paths shipped with the website."""

    root = website_root()
    return sorted(
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file()
    )


def export_website(destination: Path, *, overwrite: bool = False) -> Path:
    """Export the website assets to *destination* and return the resolved path."""

    root = website_root()
    destination = destination.expanduser().resolve()
    if destination.exists():
        if not overwrite:
            raise FileExistsError(
                f"Destination {destination} already exists. Use overwrite=True to replace it."
            )
        shutil.rmtree(destination)
    shutil.copytree(root, destination)
    return destination


def website_metadata() -> Dict[str, object]:
    """Return aggregate information about the website bundle."""

    root = website_root()
    files = list(root.rglob("*"))
    pages = [path for path in files if path.suffix == ".html"]
    assets = [path for path in files if path.is_file() and path.suffix != ".html"]
    return {
        "root": str(root),
        "file_count": len([path for path in files if path.is_file()]),
        "page_count": len(pages),
        "asset_count": len(assets),
    }


def create_website_server(*, bind: str = "127.0.0.1", port: int = 8090) -> SAPLServer:
    """Create an HTTP server that serves the bundled website."""

    root = website_root()
    return SAPLServer(bind=bind, port=port, directory=str(root))


__all__ = [
    "create_website_server",
    "export_website",
    "list_website_assets",
    "website_metadata",
    "website_root",
]
