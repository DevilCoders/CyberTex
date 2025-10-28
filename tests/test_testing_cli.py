from sapl import testing
from sapl import cli


def _write_test_file(path, body):
    path.write_text(body, encoding="utf-8")


def test_run_tests_success(tmp_path):
    script = tmp_path / "test_success.sapl"
    _write_test_file(
        script,
        """
DEF test_truth():
    RETURN TRUE
""".strip()
    )
    files = testing.discover_test_files([str(tmp_path)])
    assert script in files
    outcomes = testing.run_tests(files)
    summary = testing.summarise_outcomes(outcomes)
    assert summary["failed"] == 0
    assert summary["passed"] >= 1


def test_cli_test_command(tmp_path):
    script = tmp_path / "test_cli_failure.sapl"
    _write_test_file(
        script,
        """
DEF test_failure():
    RETURN FALSE
""".strip()
    )
    exit_code = cli.main(["test", str(script)])
    assert exit_code == 1
