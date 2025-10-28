"""Utilities for loading user-defined SAPL modules and packages."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence


@dataclass(frozen=True)
class ModuleSpec:
    """Description of where to load a module from."""

    dotted: str
    kind: str  # "module" or "package"
    path: Path


class ModuleLoader:
    """Resolve SAPL module specifications from a list of search paths."""

    def __init__(self, search_paths: Sequence[Path] | None = None) -> None:
        self.search_paths: List[Path] = []
        if search_paths:
            for path in search_paths:
                self.add_path(path)

    @classmethod
    def from_script_path(cls, script_path: Path) -> "ModuleLoader":
        return cls([script_path.parent])

    def add_path(self, path: Path) -> None:
        resolved = path.resolve()
        if resolved not in self.search_paths:
            self.search_paths.append(resolved)

    def spawn_child(self, *extra_paths: Path) -> "ModuleLoader":
        child = ModuleLoader(self.search_paths)
        for path in extra_paths:
            child.add_path(path)
        return child

    def resolve(self, module: Sequence[str]) -> Optional[ModuleSpec]:
        parts = list(module)
        dotted = ".".join(parts)
        for base in self.search_paths:
            module_path = base.joinpath(*parts)
            file_candidate = module_path.with_suffix(".sapl")
            if file_candidate.exists():
                return ModuleSpec(dotted, "module", file_candidate)
            if module_path.is_dir():
                init_candidate = module_path / "__init__.sapl"
                if init_candidate.exists():
                    return ModuleSpec(dotted, "package", init_candidate)
        return None

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"ModuleLoader(search_paths={self.search_paths!r})"


__all__ = ["ModuleLoader", "ModuleSpec"]
