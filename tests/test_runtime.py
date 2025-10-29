from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sapl.cli import run_file
from sapl.lexer import lex
from sapl.parser import parse
from sapl.runtime import Interpreter


def evaluate(source: str):
    tokens = lex(source)
    program = parse(tokens)
    interpreter = Interpreter()
    return interpreter.execute(program)


def test_block_comment_tokens_and_execution():
    source = "\n".join(
        [
            "##",
            "Block comment guidance",
            "Second line of detail",
            "##",
            'SET marker = "done"',
        ]
    )
    tokens = lex(source)
    comments = [token.value for token in tokens if token.type == "COMMENT"]
    assert any("Second line" in comment for comment in comments)

    program = parse(tokens)
    interpreter = Interpreter()
    result = interpreter.execute(program)
    assert result.variables["marker"] == "done"


def test_domain_statements_with_indentation(tmp_path: Path):
    script = tmp_path / "plan.sapl"
    script.write_text(
        "\n".join(
            [
                'TARGET ["https://one.local", "https://two.local"]',
                'SET env = "prod"',
                'TASK "Recon {env}" :',
                '    PORTSCAN [80, 443]',
                '    HTTP GET "{target}/status" EXPECT 200',
                '    NOTE "Tracking {env} hosts"',
            ]
        )
    )
    result = run_file(str(script))
    assert result.targets == ["https://one.local", "https://two.local"]
    assert result.tasks[0].name == "Recon prod"
    assert result.tasks[0].steps[0].kind == "portscan"
    assert result.tasks[0].steps[1].details["expect_status"] == 200
    assert result.notes == ["Tracking prod hosts"]


def test_control_flow_and_functions():
    source = "\n".join(
        [
            "SET counter = 0",
            "SET numbers = []",
            "DEF bump(value):",
            "    RETURN value + 1",
            "WHILE counter < 5:",
            "    counter = bump(counter)",
            "    IF counter == 3:",
            "        CONTINUE",
            "    numbers.append(counter)",
            "    IF counter == 4:",
            "        BREAK",
        ]
    )
    result = evaluate(source)
    assert result.variables["counter"] == 4
    assert result.variables["numbers"] == [1, 2, 4]


def test_standard_library_and_imports():
    source = "\n".join(
        [
            'SET encoded = json_dumps({"scope": ["app", "api"]})',
            "IMPORT math",
            "FROM statistics import mean",
            "SET root = math.sqrt(49)",
            "SET average = mean([1, 3, 5])",
        ]
    )
    result = evaluate(source)
    assert result.variables["encoded"] == '{\n  "scope": [\n    "app",\n    "api"\n  ]\n}'
    assert result.variables["root"] == 7
    assert result.variables["average"] == 3


def test_class_and_context_manager_behaviour():
    source = "\n".join(
        [
            "SET events = []",
            "CLASS Collector(object):",
            "    DEF __init__(self, sink):",
            "        self.sink = sink",
            "    DEF __enter__(self):",
            "        self.sink.append('enter')",
            "        RETURN self",
            "    DEF __exit__(self, exc_type, exc, tb):",
            "        self.sink.append('exit')",
            "        RETURN False",
            "WITH Collector(events) AS collector:",
            "    NOTE 'inside collector'",
            "SET snapshot = events",
        ]
    )
    result = evaluate(source)
    assert result.variables["snapshot"] == ["enter", "exit"]
    assert result.notes == ["inside collector"]


def test_docstrings_input_output_and_sets():
    source = "\n".join(
        [
            'TARGET ["https://demo"]',
            'SET baseline = {"http", "https"}',
            'OUTPUT "Hello {target}"',
            'INPUT "Provide operator name: " AS operator',
            'TASK "Recon":',
            '    "Document recon flow"',
            '    NOTE "Using operator {operator}"',
            'DEF helper(value):',
            '    "Return increment"',
            '    RETURN value + 1',
            'SET results = {"operator": operator, "count": helper(4)}',
            'SET pair = (1, 2)',
            '[first, second] = pair',
            'CLASS Recorder:',
            '    "Tracks docstrings"',
            '    DEF __init__(self):',
            '        PASS',
        ]
    )
    tokens = lex(source)
    program = parse(tokens)
    interpreter = Interpreter()

    outputs = []
    prompts = []

    def fake_input(prompt: str = "") -> str:
        prompts.append(prompt)
        return "analyst"

    interpreter.context.builtins["input"] = fake_input
    interpreter.context.builtins["print"] = lambda value: outputs.append(value)

    result = interpreter.execute(program)

    assert prompts == ["Provide operator name: "]
    assert outputs == ["Hello https://demo"]
    assert result.variables["operator"] == "analyst"
    assert result.variables["baseline"] == {"http", "https"}
    assert result.variables["results"] == {"operator": "analyst", "count": 5}
    assert result.variables["first"] == 1
    assert result.variables["second"] == 2
    assert result.standalone_actions[0].kind == "output"
    assert result.standalone_actions[1].kind == "input"
    assert result.standalone_actions[1].details["prompt"] == "Provide operator name: "
    assert result.tasks[0].docstring == "Document recon flow"
    helper_fn = interpreter.context.variables["helper"]
    assert helper_fn.__doc__ == "Return increment"
    recorder_cls = interpreter.context.variables["Recorder"]
    assert recorder_cls.__doc__ == "Tracks docstrings"


def test_comprehension_lambda_and_async_behaviour():
    source = "\n".join(
        [
            'TARGET ["https://one.local", "http://two.local"]',
            'IMPORT asyncio',
            'SET filtered = [host FOR host IN targets IF host.startswith("https")]',
            'SET parity = "even" IF len(filtered) % 2 == 0 ELSE "odd"',
            'SET scale = lambda value, factor=2: value * factor',
            'SET scaled = [scale(number) FOR number IN range(3)]',
            'ASYNC DEF fetch(value):',
            '    RETURN await asyncio.sleep(0, result=value + 1)',
            'SET fetched = AWAIT fetch(5)',
        ]
    )
    result = evaluate(source)
    assert result.variables["filtered"] == ["https://one.local"]
    assert result.variables["parity"] == "odd"
    assert result.variables["scaled"] == [0, 2, 4]
    assert result.variables["fetched"] == 6


def test_embed_statement_registers_assets():
    source = "\n".join(
        [
            'TARGET ["https://acme.local"]',
            'EMBED html landing = "<h1>{target}</h1>" USING {"path": "site/index.html", "tags": ["web", "demo"]}',
        ]
    )
    result = evaluate(source)
    assert "landing" in result.embedded_assets
    asset = result.embedded_assets["landing"]
    assert asset["language"] == "html"
    assert asset["metadata"]["path"] == "site/index.html"
    assert asset["metadata"]["tags"] == ["web", "demo"]
    assert asset["content"] == "<h1>https://acme.local</h1>"
    embed_actions = [action for action in result.standalone_actions if action.kind == "embed"]
    assert embed_actions and "landing" in embed_actions[0].summary


def test_extended_helper_functions(tmp_path: Path):
    file_path = tmp_path / "helpers.txt"
    source = "\n".join(
        [
            'SET raw = ["1", "2", "3"]',
            'SET ints = [to_int(item) FOR item IN raw]',
            'SET info = object_describe(ints)',
            'SET loud = string_upper("sapl")',
            'SET pipeline = pipe("  sample  ", string_strip, string_title)',
            f'SET file_path = "{file_path}"',
            'file_write_text(file_path, string_join("\\n", ["sapl", loud]))',
            'SET read_back = file_read_text(file_path)',
            'SET Custom = define_exception("CustomIssue")',
            'TRY:',
            '    RAISE Custom("boom")',
            'EXCEPT Custom AS err:',
            '    SET handled = string_title(str(err))',
            'FINALLY:',
            '    SET finished = True',
        ]
    )
    result = evaluate(source)
    assert result.variables["ints"] == [1, 2, 3]
    assert result.variables["info"]["type"] == "list"
    assert "append" in result.variables["info"]["attributes"]
    assert result.variables["loud"] == "SAPL"
    assert result.variables["pipeline"] == "Sample"
    assert result.variables["read_back"] == "sapl\nSAPL"
    assert result.variables["handled"] == "Boom"
    assert result.variables["finished"] is True
