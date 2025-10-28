"""Plugin discovery and loading utilities for SAPL."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
from typing import Callable, List, Sequence

from .errors import SAPLError

if False:  # pragma: no cover - type checking aid
    from .runtime import Interpreter

PluginHook = Callable[["Interpreter"], None]


class PluginError(SAPLError):
    """Raised when a plugin cannot be loaded or is malformed."""


def _wrap_plugin(hook: Callable[["Interpreter"], None], source: str) -> PluginHook:
    if not callable(hook):
        raise PluginError(f"Plugin entry point '{source}' is not callable")

    def wrapper(interpreter: "Interpreter") -> None:
        hook(interpreter)

    setattr(wrapper, "__sapl_plugin_name__", source)
    return wrapper


def load_plugin(spec: str) -> PluginHook:
    """Load a plugin specified as ``module[:attribute]``."""

    module_name, _, attribute = spec.partition(":")
    if not module_name:
        raise PluginError("Plugin specification must include a module name")
    module = importlib.import_module(module_name)
    if not attribute:
        attribute = "register"
    if not hasattr(module, attribute):
        raise PluginError(
            f"Plugin '{module_name}' does not expose attribute '{attribute}'"
        )
    hook = getattr(module, attribute)
    return _wrap_plugin(hook, f"{module_name}:{attribute}")


def load_plugins_from_directory(directory: Path) -> List[PluginHook]:
    """Load all plugins from ``*.py`` files within *directory*."""

    hooks: List[PluginHook] = []
    directory = directory.resolve()
    if not directory.exists():
        raise PluginError(f"Plugin directory '{directory}' does not exist")
    if not directory.is_dir():
        raise PluginError(f"Plugin path '{directory}' is not a directory")
    for index, file_path in enumerate(sorted(directory.glob("*.py"))):
        module_name = f"sapl_plugin_{file_path.stem}_{index}"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise PluginError(f"Unable to load plugin from '{file_path}'")
        module = importlib.util.module_from_spec(spec)
        loader = spec.loader
        assert loader is not None  # for type checkers
        loader.exec_module(module)  # type: ignore[call-arg]
        hook = getattr(module, "register", None)
        if hook is None:
            raise PluginError(
                f"Plugin file '{file_path}' must define a callable 'register'"
            )
        hooks.append(_wrap_plugin(hook, str(file_path)))
    return hooks


def load_plugins(
    specs: Sequence[str] | None = None,
    directories: Sequence[Path] | None = None,
) -> List[PluginHook]:
    """Return plugin hooks from module specs and directories."""

    hooks: List[PluginHook] = []
    for spec in specs or []:
        hooks.append(load_plugin(spec))
    for directory in directories or []:
        hooks.extend(load_plugins_from_directory(directory))
    return hooks


def plugin_name(hook: PluginHook) -> str:
    """Return a human-readable name for *hook*."""

    return getattr(hook, "__sapl_plugin_name__", getattr(hook, "__name__", "plugin"))


__all__ = [
    "PluginError",
    "PluginHook",
    "load_plugin",
    "load_plugins",
    "load_plugins_from_directory",
    "plugin_name",
]
