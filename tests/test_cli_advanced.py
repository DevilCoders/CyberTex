from __future__ import annotations

import json
from pathlib import Path

from sapl import cli


def test_inspect_command_json(tmp_path, capsys):
    script = tmp_path / "demo.sapl"
    script.write_text(
        "\n".join(
            [
                '"Inspection module"',
                'TARGET ["https://demo.local"]',
                'PAYLOAD probes = ["one", "two"]',
                'DEF helper(value, factor=2):',
                '    "Multiply value"',
                '    RETURN value * factor',
                'CLASS Worker:',
                '    "Stores a label"',
                '    DEF __init__(self, label):',
                '        self.label = label',
                'TASK "Audit":',
                '    "Collect baseline"',
                '    NOTE "Running"',
            ]
        )
    )
    exit_code = cli.main(["inspect", str(script), "--json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["docstring"] == "Inspection module"
    assert payload["statistics"]["functions"] >= 1
    assert any(item["name"] == "helper" for item in payload["functions"])
    assert any(item["name"] == "Worker" for item in payload["classes"])
    assert any(item["name"] == "probes" for item in payload["payloads"])
    assert any(item["name"] == "Audit" for item in payload["tasks"])


def test_shell_execute_json_output(capsys):
    exit_code = cli.main(["shell", "--execute", "SET value = 1", "--json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["variables"]["value"] == 1


def test_website_export(tmp_path, capsys):
    destination = tmp_path / "site"
    exit_code = cli.main(["website", "--export", str(destination)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Exported website assets" in captured.out
    assert destination.exists()
    assert (destination / "index.html").exists()


def test_compile_command_emits_csharp(tmp_path, capsys):
    script = tmp_path / "demo.sapl"
    script.write_text("value = 7\n")
    exit_code = cli.main(["compile", str(script), "--target", "csharp"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "public static class SaplProgram" in captured.out


def test_compile_command_emits_php(tmp_path, capsys):
    script = tmp_path / "demo.sapl"
    script.write_text("value = 9\n")
    exit_code = cli.main(["compile", str(script), "--target", "php"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "<?php" in captured.out
