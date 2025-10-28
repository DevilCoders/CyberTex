from sapl.cli import run_file


def test_imports_local_modules(tmp_path):
    package = tmp_path / "toolkit"
    package.mkdir()
    (package / "__init__.sapl").write_text(
        "DEF tag(value):\n    RETURN \"tag-\" + value\n",
        encoding="utf-8",
    )
    (package / "math_ops.sapl").write_text(
        "DEF double(value):\n    RETURN value * 2\n",
        encoding="utf-8",
    )
    script = tmp_path / "main.sapl"
    script.write_text(
        "IMPORT toolkit.math_ops AS math_ops\n"
        "FROM toolkit IMPORT tag\n"
        "SET doubled = math_ops.double(21)\n"
        "SET label = tag('demo')\n",
        encoding="utf-8",
    )

    result = run_file(str(script))
    assert result.variables["doubled"] == 42
    assert result.variables["label"] == "tag-demo"
