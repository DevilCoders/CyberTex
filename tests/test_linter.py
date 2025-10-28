from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sapl.linter import lint_source


def collect_messages(source: str):
    return lint_source(source)


def test_unused_variable_and_payload_warning():
    source = "\n".join(
        [
            'SET project = "alpha"',
            'PAYLOAD fuzzers = ["a"]',
            'NOTE "{project}"',
        ]
    )
    messages = collect_messages(source)
    descriptions = {message.message for message in messages}
    assert "Payload 'fuzzers' is defined but never used" in descriptions
    assert "Variable 'project' is defined but never used" not in descriptions


def test_undefined_payload_and_identifier_errors():
    source = "\n".join(
        [
            'RUN helper',
            'FUZZ "https://example.com" METHOD POST USING missing_payload',
        ]
    )
    messages = collect_messages(source)
    errors = [message.message for message in messages if message.severity == "ERROR"]
    assert "Identifier 'helper' is not defined" in errors
    assert "Payload 'missing_payload' is not defined" in errors


def test_loop_placeholder_not_reported():
    source = "\n".join(
        [
            'TARGET ["https://one.local", "https://two.local"]',
            'FOR host IN targets:',
            '    NOTE "Checking {host}"',
        ]
    )
    messages = collect_messages(source)
    assert not messages


def test_break_outside_loop_flagged():
    messages = collect_messages("BREAK")
    assert any(message.message == "BREAK used outside of a loop" for message in messages)


def test_linter_handles_comprehension_lambda_and_async():
    source = "\n".join(
        [
            'IMPORT asyncio',
            'SET baseline = [value FOR value IN [0, 1, 2] IF value]',
            'SET status = "non-empty" IF baseline ELSE "empty"',
            'SET mapper = lambda item, step=1: item + step',
            'SET transformed = [mapper(item) FOR item IN baseline]',
            'ASYNC DEF compute(value):',
            '    RETURN await asyncio.sleep(0, result=value * 2)',
            'SET awaited = AWAIT compute(2)',
            'NOTE "Awaited value {awaited} with {transformed} during {status}"',
        ]
    )
    messages = collect_messages(source)
    assert not messages
