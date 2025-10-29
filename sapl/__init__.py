"""SAPL (Special Advanced Programming Language) package."""

from .import_hooks import install_sapl_importer

install_sapl_importer()

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
from .stdlib import STANDARD_LIBRARY_CATALOG
from .server import SAPLServer
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
