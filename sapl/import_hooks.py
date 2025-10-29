"""Import helpers that allow Python source stored in `.sapl` files."""

from __future__ import annotations

import importlib.machinery
import sys
from functools import lru_cache

SAPL_SOURCE_SUFFIX = ".sapl"


def _build_file_finder_hook() -> importlib.machinery.FileFinder.path_hook:
    """Return a FileFinder path hook aware of `.sapl` sources."""

    loader_details = (
        (importlib.machinery.SourceFileLoader, importlib.machinery.SOURCE_SUFFIXES),
        (importlib.machinery.SourcelessFileLoader, importlib.machinery.BYTECODE_SUFFIXES),
        (importlib.machinery.ExtensionFileLoader, importlib.machinery.EXTENSION_SUFFIXES),
    )
    hook = importlib.machinery.FileFinder.path_hook(*loader_details)
    setattr(hook, "__sapl_hook__", True)
    return hook


@lru_cache(maxsize=1)
def _sapl_file_finder_hook() -> importlib.machinery.FileFinder.path_hook:
    return _build_file_finder_hook()


def install_sapl_importer() -> None:
    """Ensure the import system can load modules from `.sapl` files."""

    if SAPL_SOURCE_SUFFIX not in importlib.machinery.SOURCE_SUFFIXES:
        importlib.machinery.SOURCE_SUFFIXES.append(SAPL_SOURCE_SUFFIX)

    hook = _sapl_file_finder_hook()
    replaced = False
    for index, existing in enumerate(sys.path_hooks):
        if getattr(existing, "__sapl_hook__", False) or getattr(
            existing, "__name__", ""
        ) == "path_hook_for_FileFinder":
            sys.path_hooks[index] = hook
            replaced = True
    if not replaced:
        sys.path_hooks.insert(0, hook)
    sys.path_importer_cache.clear()


__all__ = ["install_sapl_importer", "SAPL_SOURCE_SUFFIX"]
