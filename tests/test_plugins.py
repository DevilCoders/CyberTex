import textwrap

import pytest

from sapl.plugins import PluginError, load_plugin, load_plugins_from_directory
from sapl.runtime import Interpreter


def test_load_plugin_from_directory(tmp_path):
    plugin = tmp_path / "demo.py"
    plugin.write_text(
        textwrap.dedent(
            """
            def register(interpreter):
                interpreter.register_builtin("demo_helper", lambda: "ok")
            """
        )
    )
    hooks = load_plugins_from_directory(tmp_path)
    assert len(hooks) == 1
    interpreter = Interpreter()
    hooks[0](interpreter)
    assert interpreter.context.builtins["demo_helper"]() == "ok"
    assert "demo_helper" in interpreter.context.builtins


def test_load_plugin_module(monkeypatch, tmp_path):
    module = tmp_path / "plugmod.py"
    module.write_text(
        textwrap.dedent(
            """
            def register(interpreter):
                interpreter.register_builtin("plug_flag", lambda: True)
            """
        )
    )
    monkeypatch.syspath_prepend(tmp_path)
    hook = load_plugin("plugmod")
    interpreter = Interpreter()
    hook(interpreter)
    assert interpreter.context.builtins["plug_flag"]()


def test_invalid_plugin_raises(tmp_path):
    module = tmp_path / "bad.py"
    module.write_text("VALUE = 1\n")
    with pytest.raises(PluginError):
        load_plugins_from_directory(tmp_path)
