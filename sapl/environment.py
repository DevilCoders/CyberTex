"""Environment helpers for SAPL projects."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import venv


REQUIRED_MANIFEST = Path(__file__).with_name("required.yaml")


def load_required_config(path: Path | None = None) -> Dict[str, List[str]]:
    """Parse the lightweight YAML requirements manifest."""

    if path is None:
        path = REQUIRED_MANIFEST
    data: Dict[str, List[str]] = {}
    current: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(":"):
            current = line[:-1]
            data[current] = []
            continue
        if line.startswith("-") and current is not None:
            data[current].append(line[1:].strip())
            continue
        raise ValueError(f"Malformed requirements line: {raw_line!r}")
    return data


def create_virtual_environment(
    destination: Path,
    *,
    copy_requirements: bool = True,
) -> Path:
    """Create a Python virtual environment primed for SAPL tooling."""

    builder = venv.EnvBuilder(with_pip=False)
    builder.create(str(destination))
    if copy_requirements:
        target_manifest = destination / "sapl-required.yaml"
        target_manifest.write_text(REQUIRED_MANIFEST.read_text(encoding="utf-8"), encoding="utf-8")
    return destination.resolve()


__all__ = ["create_virtual_environment", "load_required_config"]
