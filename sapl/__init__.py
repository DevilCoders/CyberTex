"""SAPL (Special Advanced Programming Language) package."""

from __future__ import annotations

import importlib.machinery as _machinery
import importlib.util as _import_util
from pathlib import Path as _Path
import sys as _sys

_SAPL_SUFFIX = ".sapl"
if _SAPL_SUFFIX not in _machinery.SOURCE_SUFFIXES:
    _machinery.SOURCE_SUFFIXES.append(_SAPL_SUFFIX)

_package_dir = _Path(__file__).resolve().parent


def _load_bootstrap_module(relative_name: str):
    """Load a bootstrap module stored as `.sapl` before the importer exists."""

    module_name = f"{__name__}.{relative_name}"
    file_path = _package_dir / f"{relative_name}.sapl"
    loader = _machinery.SourceFileLoader(module_name, str(file_path))
    spec = _import_util.spec_from_loader(module_name, loader)
    module = _import_util.module_from_spec(spec)
    loader.exec_module(module)
    _sys.modules[module_name] = module
    return module


_import_hooks = _load_bootstrap_module("import_hooks")
install_sapl_importer = _import_hooks.install_sapl_importer
install_sapl_importer()

del (
    _import_hooks,
    _load_bootstrap_module,
    _machinery,
    _import_util,
    _Path,
    _package_dir,
    _SAPL_SUFFIX,
    _sys,
)

from .advanced_compiler import AdvancedCompiler
from .cli import highlight_file, lint_file, run_file
from .environment import create_virtual_environment, load_required_config
from .highlight import available_themes, highlight_source
from .linter import lint_source
from .module_loader import ModuleLoader
from .plugins import (
    PluginError,
    load_plugin,
    load_plugins,
    load_plugins_from_directory,
)
from .server import SAPLServer
from .stdlib import STANDARD_LIBRARY_CATALOG
from .testing import discover_test_files, run_tests, summarise_outcomes

__all__ = [
    "AdvancedCompiler",
    "available_themes",
    "create_virtual_environment",
    "highlight_file",
    "highlight_source",
    "lint_file",
    "lint_source",
    "load_required_config",
    "load_plugin",
    "load_plugins",
    "load_plugins_from_directory",
    "ModuleLoader",
    "PluginError",
    "discover_test_files",
    "run_file",
    "SAPLServer",
    "STANDARD_LIBRARY_CATALOG",
    "install_sapl_importer",
    "run_tests",
    "summarise_outcomes",
]
