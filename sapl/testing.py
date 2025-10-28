"""Testing helpers powering the ``sapl-test`` workflow."""

from __future__ import annotations

import time
import traceback
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Sequence

from .lexer import lex
from .module_loader import ModuleLoader
from .parser import parse
from .plugins import PluginHook
from .runtime import Interpreter, PendingAsyncCall, SAPLFunction


@dataclass
class TestOutcome:
    """Represents the result of executing a single SAPL test function."""

    path: Path
    name: str
    status: str
    duration: float
    message: str | None = None

    @property
    def success(self) -> bool:
        return self.status == "passed"

    def as_dict(self) -> dict:
        payload = asdict(self)
        payload["path"] = str(self.path)
        return payload


def discover_test_files(targets: Sequence[str] | None = None) -> List[Path]:
    """Discover SAPL test files based on ``test_*.sapl`` patterns."""

    if not targets:
        targets = [str(Path.cwd())]
    discovered: List[Path] = []
    seen: set[Path] = set()
    for target in targets:
        path = Path(target).resolve()
        if path.is_file() and path.suffix == ".sapl":
            if path not in seen:
                discovered.append(path)
                seen.add(path)
            continue
        if not path.is_dir():
            continue
        patterns = ("test_*.sapl", "*_test.sapl")
        for pattern in patterns:
            for candidate in sorted(path.rglob(pattern)):
                resolved = candidate.resolve()
                if resolved in seen:
                    continue
                discovered.append(resolved)
                seen.add(resolved)
    return discovered


def run_tests(
    files: Sequence[Path],
    *,
    plugins: Sequence[PluginHook] | None = None,
) -> List[TestOutcome]:
    """Execute SAPL test functions within *files*."""

    outcomes: List[TestOutcome] = []
    plugin_hooks = list(plugins or [])
    for file_path in files:
        source = file_path.read_text(encoding="utf-8")
        program = parse(lex(source))
        loader = ModuleLoader.from_script_path(file_path)
        interpreter = Interpreter(module_loader=loader, plugins=plugin_hooks)
        interpreter.execute(program)
        tests: List[tuple[str, SAPLFunction]] = []
        for name, value in interpreter.context.variables.items():
            if isinstance(value, SAPLFunction) and name.startswith("test_"):
                tests.append((name, value))
        if not tests:
            outcomes.append(
                TestOutcome(
                    path=file_path,
                    name="<no tests>",
                    status="skipped",
                    duration=0.0,
                    message="No test functions discovered",
                )
            )
            continue
        for name, function in sorted(tests, key=lambda item: item[0]):
            start = time.perf_counter()
            status = "passed"
            message: str | None = None
            try:
                result = function()
                while isinstance(result, PendingAsyncCall):
                    result = result.resolve()
                if result is False:
                    status = "failed"
                    message = "Returned falsy result"
                elif result not in (None, True):
                    try:
                        if not bool(result):
                            status = "failed"
                            message = f"Returned falsy result {result!r}"
                    except Exception:  # pragma: no cover - bool override raised
                        status = "failed"
                        message = f"Result {result!r} could not be evaluated as truthy"
            except Exception as exc:  # pylint: disable=broad-except
                status = "failed"
                message = "".join(
                    traceback.format_exception_only(type(exc), exc)
                ).strip()
            duration = time.perf_counter() - start
            outcomes.append(
                TestOutcome(
                    path=file_path,
                    name=name,
                    status=status,
                    duration=duration,
                    message=message,
                )
            )
    return outcomes


def summarise_outcomes(outcomes: Sequence[TestOutcome]) -> dict:
    """Return aggregate statistics for *outcomes*."""

    total_duration = sum(outcome.duration for outcome in outcomes)
    summary = {
        "total": len(outcomes),
        "passed": sum(1 for outcome in outcomes if outcome.status == "passed"),
        "failed": sum(1 for outcome in outcomes if outcome.status == "failed"),
        "skipped": sum(1 for outcome in outcomes if outcome.status == "skipped"),
        "duration": total_duration,
    }
    return summary


__all__ = [
    "TestOutcome",
    "discover_test_files",
    "run_tests",
    "summarise_outcomes",
]
