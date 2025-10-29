"""Command line interface for running SAPL programs."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence

from . import testing
from .advanced_compiler import AdvancedCompiler
from .backends import (
    AssemblyEmitter,
    BytecodeCompiler,
    CLanguageEmitter,
    CSharpEmitter,
    CppEmitter,
    GoEmitter,
    JavaEmitter,
    JavaScriptEmitter,
    MachineCodeCompiler,
    PerlEmitter,
    PhpEmitter,
    REmitter,
    RubyEmitter,
    RustEmitter,
    SqlEmitter,
    Transpiler,
)
from .environment import create_virtual_environment, load_required_config
from .errors import SAPLError
from .highlight import available_themes, highlight_source
from .inspector import inspect_path
from .linter import LintMessage, lint_source
from .lexer import lex
from .module_loader import ModuleLoader
from .plugins import PluginError, load_plugins
from .parser import parse
from .repl import SAPLRepl, delta_to_dict
from .runtime import ExecutionResult, Interpreter
from .server import SAPLServer
from .website_manager import (
    create_website_server,
    export_website,
    list_website_assets,
    website_metadata,
)


def run_file(
    path: str,
    *,
    plugins: Sequence[Callable[[Interpreter], None]] | None = None,
) -> ExecutionResult:
    """Parse and execute a SAPL script from the filesystem."""

    script_path = Path(path).resolve()
    with script_path.open("r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    interpreter = Interpreter(
        module_loader=ModuleLoader.from_script_path(script_path),
        plugins=plugins,
    )
    return interpreter.execute(program)


def lint_file(path: str) -> List[LintMessage]:
    """Run the SAPL linter against a script file."""

    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    return lint_source(source)


def highlight_file(path: str, theme: str = "dark") -> str:
    """Return a highlighted representation of a SAPL script."""

    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    return highlight_source(source, theme=theme)


def compile_machine_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    compiled = MachineCodeCompiler().compile(program)
    return compiled.render()


def compile_bytecode_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    compiled = BytecodeCompiler().compile(program)
    instructions = [[opcode, operand] for opcode, operand in compiled.instructions]
    return {"instructions": instructions, "constants": compiled.constants}


def transpile_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return Transpiler().transpile(program)


def emit_assembly_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return AssemblyEmitter().emit(program)


def emit_c_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return CLanguageEmitter().emit(program)


def emit_cpp_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return CppEmitter().emit(program)


def emit_csharp_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return CSharpEmitter().emit(program)


def emit_php_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return PhpEmitter().emit(program)


def emit_sql_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return SqlEmitter().emit(program)


def emit_go_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return GoEmitter().emit(program)


def emit_java_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return JavaEmitter().emit(program)


def emit_javascript_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return JavaScriptEmitter().emit(program)


def emit_perl_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return PerlEmitter().emit(program)


def emit_rust_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return RustEmitter().emit(program)


def emit_ruby_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return RubyEmitter().emit(program)


def emit_r_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    tokens = lex(source)
    program = parse(tokens)
    return REmitter().emit(program)


def format_result(result: ExecutionResult) -> str:
    """Convert an execution result into a human-readable report."""

    lines: List[str] = []
    if result.targets:
        lines.append("Targets: " + ", ".join(result.targets))
    if result.scope:
        lines.append("Scope: " + ", ".join(result.scope))
    if result.variables:
        rendered_vars = ", ".join(f"{name}={value}" for name, value in result.variables.items())
        lines.append(f"Variables: {rendered_vars}")
    if result.payloads:
        for name, payloads in result.payloads.items():
            lines.append(f"Payload {name}: {', '.join(payloads)}")
    if result.embedded_assets:
        lines.append("\nEmbedded assets:")
        for name, asset in result.embedded_assets.items():
            language = asset.get("language", "unknown")
            entry = f"  - {name} [{language}]"
            metadata = asset.get("metadata") or {}
            if metadata:
                entry += f" meta={metadata}"
            content = asset.get("content")
            if isinstance(content, bytes):
                preview_source = content.decode("utf-8", "replace")
            else:
                preview_source = str(content)
            preview = preview_source.strip()
            if preview:
                entry += f" => {preview[:60]}{'…' if len(preview) > 60 else ''}"
            lines.append(entry)
    for task in result.tasks:
        lines.append(f"\nTask: {task.name}")
        for action in task.steps:
            lines.append(f"  - [{action.kind}] {action.summary}")
            for key, value in action.details.items():
                lines.append(f"      {key}: {value}")
    if result.standalone_actions:
        lines.append("\nGeneral actions:")
        for action in result.standalone_actions:
            lines.append(f"  - [{action.kind}] {action.summary}")
            for key, value in action.details.items():
                lines.append(f"      {key}: {value}")
    if result.notes:
        lines.append("\nNotes:")
        for note in result.notes:
            lines.append(f"  - {note}")
    if result.findings:
        lines.append("\nFindings:")
        for finding in result.findings:
            lines.append(f"  - ({finding.severity}) {finding.message}")
    if result.report_destination:
        lines.append(f"\nReport destination: {result.report_destination}")
    return "\n".join(lines)


def result_to_dict(result: ExecutionResult) -> dict:
    """Represent the execution result as a JSON-serialisable dict."""

    return asdict(result)


def _resolve_plugins(
    plugin_specs: Sequence[str], plugin_dirs: Sequence[str]
) -> List[Callable[[Interpreter], None]]:
    directories = [Path(directory) for directory in plugin_dirs]
    return load_plugins(plugin_specs, directories)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Utilities for SAPL scripts")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Execute a SAPL script")
    run_parser.add_argument("script", help="Path to the SAPL script")
    run_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the execution plan as JSON instead of text",
    )
    run_parser.add_argument(
        "--lint",
        action="store_true",
        help="Lint the script before executing it",
    )
    run_parser.add_argument(
        "--plugin",
        action="append",
        default=[],
        help="Load a plugin specified as module[:callable]",
    )
    run_parser.add_argument(
        "--plugin-dir",
        action="append",
        default=[],
        help="Discover Python plugins from a directory",
    )

    lint_parser = subparsers.add_parser("lint", help="Run the SAPL linter")
    lint_parser.add_argument("script", help="Path to the SAPL script")
    lint_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit lint diagnostics as JSON",
    )

    theme_choices = sorted(available_themes().keys())
    highlight_parser = subparsers.add_parser("highlight", help="Syntax highlight a SAPL script")
    highlight_parser.add_argument("script", help="Path to the SAPL script")
    highlight_parser.add_argument(
        "--theme",
        default="dark",
        choices=theme_choices,
        help="Colour theme to use for highlighting",
    )

    compile_parser = subparsers.add_parser("compile", help="Compile a SAPL script using backend targets")
    compile_parser.add_argument("script", help="Path to the SAPL script")
    compile_parser.add_argument(
        "--target",
        default="machine",
        choices=[
            "machine",
            "bytecode",
            "python",
            "assembly",
            "c",
            "cpp",
            "csharp",
            "php",
            "sql",
            "go",
            "java",
            "javascript",
            "perl",
            "rust",
            "ruby",
            "r",
        ],
        help="Compilation target to emit",
    )

    adv_parser = subparsers.add_parser(
        "advanced-compile",
        help="Compile a SAPL script while emitting structural metadata",
    )
    adv_parser.add_argument("script", help="Path to the SAPL script")
    adv_parser.add_argument(
        "--target",
        default="machine",
        choices=[
            "machine",
            "bytecode",
            "python",
            "assembly",
            "c",
            "cpp",
            "csharp",
            "php",
            "sql",
            "go",
            "java",
            "javascript",
            "perl",
            "rust",
            "ruby",
            "r",
        ],
        help="Compilation target to emit",
    )
    adv_parser.add_argument(
        "--opt-level",
        type=int,
        default=1,
        help="Optimization level hint for the advanced compiler",
    )
    adv_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the advanced compile artifact as JSON",
    )

    test_parser = subparsers.add_parser("test", help="Run SAPL test suites")
    test_parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories containing SAPL tests",
    )
    test_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit test results as JSON",
    )
    test_parser.add_argument(
        "--plugin",
        action="append",
        default=[],
        help="Load a plugin specified as module[:callable] before running tests",
    )
    test_parser.add_argument(
        "--plugin-dir",
        action="append",
        default=[],
        help="Discover Python plugins from a directory",
    )

    serve_parser = subparsers.add_parser(
        "serve", help="Run the built-in SAPL HTTP server"
    )
    serve_parser.add_argument(
        "--bind",
        default="127.0.0.1",
        help="Interface address to bind",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number to listen on",
    )
    serve_parser.add_argument(
        "--directory",
        default=".",
        help="Directory to expose over HTTP",
    )
    serve_parser.add_argument(
        "--once",
        action="store_true",
        help="Serve a single request and exit",
    )

    venv_parser = subparsers.add_parser(
        "venv", help="Create a virtual environment primed for SAPL"
    )
    venv_parser.add_argument("path", help="Destination directory for the virtual environment")
    venv_parser.add_argument(
        "--no-requirements",
        action="store_true",
        help="Skip copying sapl-required.yaml into the environment",
    )
    venv_parser.add_argument(
        "--print-required",
        action="store_true",
        help="Print the parsed required.yaml manifest after creation",
    )

    inspect_parser = subparsers.add_parser(
        "inspect", help="Analyse a SAPL script and report its structure"
    )
    inspect_parser.add_argument("script", help="Path to the SAPL script")
    inspect_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the inspection summary as JSON",
    )

    shell_parser = subparsers.add_parser(
        "shell", help="Start an interactive SAPL shell"
    )
    shell_parser.add_argument(
        "--execute",
        action="append",
        default=[],
        help="Execute a snippet of SAPL code and exit",
    )
    shell_parser.add_argument(
        "--script",
        action="append",
        default=[],
        help="Preload and execute a SAPL script before starting the shell",
    )
    shell_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit shell deltas as JSON when using --execute",
    )
    shell_parser.add_argument(
        "--plugin",
        action="append",
        default=[],
        help="Load a plugin specified as module[:callable] before executing snippets",
    )
    shell_parser.add_argument(
        "--plugin-dir",
        action="append",
        default=[],
        help="Discover Python plugins from a directory",
    )

    website_parser = subparsers.add_parser(
        "website", help="Manage the bundled SAPL advanced website"
    )
    website_parser.add_argument(
        "--list",
        action="store_true",
        help="List the files shipped with the website bundle",
    )
    website_parser.add_argument(
        "--export",
        help="Export the website assets to a directory",
    )
    website_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the export directory if it already exists",
    )
    website_parser.add_argument(
        "--serve",
        action="store_true",
        help="Serve the website using the built-in HTTP server",
    )
    website_parser.add_argument(
        "--bind",
        default="127.0.0.1",
        help="Interface address to bind when serving",
    )
    website_parser.add_argument(
        "--port",
        type=int,
        default=8090,
        help="Port number to use when serving",
    )

    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)
    commands = {
        "run",
        "lint",
        "highlight",
        "compile",
        "advanced-compile",
        "serve",
        "venv",
        "test",
        "inspect",
        "shell",
        "website",
    }
    if argv and argv[0] not in commands:
        argv = ["run", *argv]
    args = parser.parse_args(argv)

    if args.command == "lint":
        return _handle_lint(args.script, emit_json=args.json)
    if args.command == "highlight":
        return _handle_highlight(args.script, theme=args.theme)
    if args.command == "compile":
        return _handle_compile(args.script, target=args.target)
    if args.command == "advanced-compile":
        return _handle_advanced_compile(
            args.script,
            target=args.target,
            opt_level=args.opt_level,
            emit_json=args.json,
        )
    if args.command == "inspect":
        return _handle_inspect(args.script, emit_json=args.json)
    if args.command == "test":
        return _handle_test(
            args.paths,
            emit_json=args.json,
            plugin_specs=args.plugin,
            plugin_dirs=args.plugin_dir,
        )
    if args.command == "serve":
        return _handle_serve(
            bind=args.bind,
            port=args.port,
            directory=args.directory,
            once=args.once,
        )
    if args.command == "venv":
        return _handle_venv(
            path=args.path,
            copy_requirements=not args.no_requirements,
            print_required=args.print_required,
        )
    if args.command == "shell":
        return _handle_shell(
            execute_snippets=args.execute,
            script_paths=args.script,
            emit_json=args.json,
            plugin_specs=args.plugin,
            plugin_dirs=args.plugin_dir,
        )
    if args.command == "website":
        return _handle_website(
            list_assets=args.list,
            export_path=args.export,
            overwrite=args.overwrite,
            serve=args.serve,
            bind=args.bind,
            port=args.port,
        )
    # default: run
    return _handle_run(
        args.script,
        emit_json=args.json,
        lint_before=args.lint,
        plugin_specs=args.plugin,
        plugin_dirs=args.plugin_dir,
    )


def _handle_run(
    script: str,
    *,
    emit_json: bool,
    lint_before: bool,
    plugin_specs: Sequence[str],
    plugin_dirs: Sequence[str],
) -> int:
    try:
        plugins = _resolve_plugins(plugin_specs, plugin_dirs)
    except PluginError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if lint_before:
        messages = lint_file(script)
        if messages:
            _print_lint(messages, emit_json=False, stream=sys.stderr)
            if any(message.severity == "ERROR" for message in messages):
                return 2
    try:
        result = run_file(script, plugins=plugins)
    except SAPLError as exc:  # pragma: no cover - CLI convenience
        print(str(exc), file=sys.stderr)
        return 1
    if emit_json:
        print(json.dumps(result_to_dict(result), indent=2))
    else:
        output = format_result(result)
        if output:
            print(output)
    return 0


def _handle_lint(script: str, *, emit_json: bool) -> int:
    try:
        messages = lint_file(script)
    except SAPLError as exc:  # pragma: no cover - CLI convenience
        print(str(exc), file=sys.stderr)
        return 1
    _print_lint(messages, emit_json=emit_json)
    has_errors = any(message.severity == "ERROR" for message in messages)
    return 1 if has_errors else 0


def _handle_highlight(script: str, *, theme: str) -> int:
    try:
        coloured = highlight_file(script, theme=theme)
    except SAPLError as exc:  # pragma: no cover - CLI convenience
        print(str(exc), file=sys.stderr)
        return 1
    print(coloured, end="")
    return 0


def _handle_compile(script: str, *, target: str) -> int:
    try:
        if target == "machine":
            output = compile_machine_file(script)
            print(output)
            return 0
        if target == "bytecode":
            payload = compile_bytecode_file(script)
            print(json.dumps(payload, indent=2))
            return 0
        if target == "python":
            python_source = transpile_file(script)
            print(python_source, end="")
            return 0
        if target == "assembly":
            listing = emit_assembly_file(script)
            print(listing, end="")
            return 0
        if target == "c":
            print(emit_c_file(script), end="")
            return 0
        if target == "cpp":
            print(emit_cpp_file(script), end="")
            return 0
        if target == "csharp":
            print(emit_csharp_file(script), end="")
            return 0
        if target == "php":
            print(emit_php_file(script), end="")
            return 0
        if target == "sql":
            print(emit_sql_file(script), end="")
            return 0
        if target == "go":
            print(emit_go_file(script), end="")
            return 0
        if target == "java":
            print(emit_java_file(script), end="")
            return 0
        if target == "javascript":
            print(emit_javascript_file(script), end="")
            return 0
        if target == "perl":
            print(emit_perl_file(script), end="")
            return 0
        if target == "rust":
            print(emit_rust_file(script), end="")
            return 0
        if target == "ruby":
            print(emit_ruby_file(script), end="")
            return 0
        if target == "r":
            print(emit_r_file(script), end="")
            return 0
        raise ValueError(f"Unknown compilation target: {target}")
    except SAPLError as exc:  # pragma: no cover - CLI convenience
        print(str(exc), file=sys.stderr)
        return 1


def _handle_advanced_compile(
    script: str,
    *,
    target: str,
    opt_level: int,
    emit_json: bool,
) -> int:
    compiler = AdvancedCompiler(optimization_level=opt_level)
    artifact = compiler.compile_path(Path(script), target=target)
    if emit_json:
        print(json.dumps(artifact.serialise(), indent=2))
    else:
        print(artifact.pretty())
    return 0


def _handle_inspect(script: str, *, emit_json: bool) -> int:
    try:
        summary = inspect_path(Path(script))
    except FileNotFoundError:
        print(f"File not found: {script}", file=sys.stderr)
        return 1
    except SAPLError as exc:  # pragma: no cover - CLI convenience
        print(str(exc), file=sys.stderr)
        return 1
    if emit_json:
        print(json.dumps(summary.as_dict(), indent=2))
        return 0
    print(_format_inspection(summary))
    return 0


def _handle_test(
    paths: Sequence[str],
    *,
    emit_json: bool,
    plugin_specs: Sequence[str],
    plugin_dirs: Sequence[str],
) -> int:
    try:
        plugins = _resolve_plugins(plugin_specs, plugin_dirs)
    except PluginError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    files = testing.discover_test_files(paths)
    if not files:
        print("No SAPL test files discovered.", file=sys.stderr)
        return 1
    outcomes = testing.run_tests(files, plugins=plugins)
    summary = testing.summarise_outcomes(outcomes)
    if emit_json:
        payload = {
            "summary": summary,
            "outcomes": [outcome.as_dict() for outcome in outcomes],
        }
        print(json.dumps(payload, indent=2))
    else:
        _print_test_report(outcomes, summary)
    return 0 if summary["failed"] == 0 else 1


def _handle_serve(*, bind: str, port: int, directory: str, once: bool) -> int:
    server = SAPLServer(bind=bind, port=port, directory=directory)
    if once:
        with server:
            server.handle_once()
        return 0
    try:
        with server:
            server.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - CLI convenience
        return 0
    return 0


def _handle_venv(*, path: str, copy_requirements: bool, print_required: bool) -> int:
    env_path = create_virtual_environment(
        Path(path), copy_requirements=copy_requirements
    )
    if print_required:
        manifest = load_required_config()
        print(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"Virtual environment created at {env_path}")
    return 0


def _handle_shell(
    *,
    execute_snippets: Sequence[str],
    script_paths: Sequence[str],
    emit_json: bool,
    plugin_specs: Sequence[str],
    plugin_dirs: Sequence[str],
) -> int:
    try:
        plugins = _resolve_plugins(plugin_specs, plugin_dirs)
    except PluginError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    repl = SAPLRepl(plugins=plugins)
    status = 0
    for path_text in script_paths:
        try:
            delta = repl.load_script(Path(path_text))
        except FileNotFoundError:
            print(f"Script not found: {path_text}", file=sys.stderr)
            status = 1
            continue
        except SAPLError as exc:
            print(str(exc), file=sys.stderr)
            status = 1
            continue
        if emit_json:
            print(json.dumps(delta_to_dict(delta), indent=2))
        else:
            rendered = repl.render_delta(delta)
            if rendered:
                print(rendered)
            print(f"Loaded {path_text}")
    if execute_snippets:
        for snippet in execute_snippets:
            try:
                delta = repl.execute_snippet(snippet)
            except SAPLError as exc:
                print(str(exc), file=sys.stderr)
                return 1
            if emit_json:
                print(json.dumps(delta_to_dict(delta), indent=2))
            else:
                rendered = repl.render_delta(delta)
                if rendered:
                    print(rendered)
        return status
    repl.run_interactive()
    return status


def _handle_website(
    *,
    list_assets: bool,
    export_path: str | None,
    overwrite: bool,
    serve: bool,
    bind: str,
    port: int,
) -> int:
    try:
        metadata = website_metadata()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    status = 0
    if not list_assets and not export_path and not serve:
        print(_format_website_metadata(metadata))
        return 0
    if list_assets:
        assets = list_website_assets()
        for asset in assets:
            print(asset)
    if export_path:
        try:
            destination = export_website(Path(export_path), overwrite=overwrite)
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            status = 1
        else:
            print(f"Exported website assets to {destination}")
    if serve:
        server = create_website_server(bind=bind, port=port)
        address = server.server_address
        url = f"http://{address[0]}:{address[1]}"
        print(f"Serving SAPL website at {url} (press Ctrl+C to stop)")
        try:
            with server:
                server.serve_forever()
        except KeyboardInterrupt:  # pragma: no cover - CLI convenience
            print("\nStopping website server")
        return status
    return status


def _print_lint(messages: List[LintMessage], *, emit_json: bool, stream=sys.stdout) -> None:
    if emit_json:
        payload = [asdict(message) for message in messages]
        print(json.dumps(payload, indent=2), file=stream)
        return
    for message in messages:
        print(message.format(), file=stream)


def _print_test_report(
    outcomes: Sequence[testing.TestOutcome],
    summary: dict | None = None,
) -> None:
    if summary is None:
        summary = testing.summarise_outcomes(outcomes)
    for outcome in outcomes:
        location = str(outcome.path)
        if outcome.name != "<no tests>":
            location = f"{location}::{outcome.name}"
        line = f"[{outcome.status.upper()}] {location} ({outcome.duration:.3f}s)"
        if outcome.message:
            line += f" - {outcome.message}"
        print(line)
    print(
        f"\nSummary: {summary['passed']} passed, {summary['failed']} failed, {summary['skipped']} skipped in {summary['duration']:.3f}s"
    )


def _format_inspection(summary) -> str:
    lines = []
    if summary.path:
        lines.append(f"Inspection summary for {summary.path}")
    else:
        lines.append("Inspection summary")
    if summary.docstring:
        lines.append(f"Docstring: {summary.docstring}")
    if summary.imports:
        lines.append("\nImports:")
        for item in summary.imports:
            alias = f" as {item.alias}" if item.alias and item.alias != item.module else ""
            lines.append(f"  - {item.module}{alias} (line {item.line})")
    if summary.variables:
        lines.append("\nVariables:")
        for variable in summary.variables:
            lines.append(
                f"  - {variable.name} [{variable.kind}] (line {variable.line}, scope {variable.scope})"
            )
    if summary.payloads:
        lines.append("\nPayloads:")
        for payload in summary.payloads:
            lines.append(f"  - {payload.name} = {payload.expression} (line {payload.line})")
    if summary.embedded_assets:
        lines.append("\nEmbedded assets:")
        for asset in summary.embedded_assets:
            meta = f" meta={asset.metadata}" if asset.metadata else ""
            lines.append(
                f"  - {asset.name} [{asset.language}] (line {asset.line}, scope {asset.scope}){meta}"
            )
            preview = asset.content
            if preview:
                trimmed = preview[:70] + ("…" if len(preview) > 70 else "")
                lines.append(f"      {trimmed}")
    if summary.directives:
        lines.append("\nDirectives:")
        for directive in summary.directives:
            lines.append(
                f"  - {directive.kind} {directive.expression} (line {directive.line})"
            )
    if summary.functions:
        lines.append("\nFunctions:")
        for function in summary.functions:
            params = ", ".join(
                f"{param.name}{'=' + param.default if param.has_default and param.default else ''}"
                for param in function.parameters
            )
            prefix = "async " if function.is_async else ""
            lines.append(
                f"  - {prefix}{function.name}({params}) (line {function.line}, scope {function.scope})"
            )
            if function.docstring:
                lines.append(f"      {function.docstring}")
    if summary.classes:
        lines.append("\nClasses:")
        for klass in summary.classes:
            bases = f" : {', '.join(klass.bases)}" if klass.bases else ""
            lines.append(
                f"  - {klass.name}{bases} (line {klass.line}, scope {klass.scope})"
            )
            if klass.docstring:
                lines.append(f"      {klass.docstring}")
    if summary.tasks:
        lines.append("\nTasks:")
        for task in summary.tasks:
            lines.append(
                f"  - {task.name} (line {task.line}, scope {task.scope})"
            )
            if task.docstring:
                lines.append(f"      {task.docstring}")
    lines.append("\nStatistics:")
    for key, value in sorted(summary.statistics.items()):
        lines.append(f"  {key}: {value}")
    return "\n".join(lines)


def _format_website_metadata(metadata: Dict[str, object]) -> str:
    lines = ["SAPL advanced website bundle:"]
    for key in ["root", "file_count", "page_count", "asset_count"]:
        value = metadata.get(key)
        lines.append(f"  {key.replace('_', ' ').title()}: {value}")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
