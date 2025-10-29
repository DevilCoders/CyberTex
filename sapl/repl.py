"""Interactive shell utilities for the SAPL command line."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

from .errors import SAPLError
from .lexer import lex
from .module_loader import ModuleLoader
from .parser import parse
from .runtime import Action, Finding, Interpreter, Task


@dataclass
class ShellDelta:
    """Summarises state changes produced by executing a snippet."""

    variables: Dict[str, object]
    targets: List[str]
    scope: List[str]
    payloads: Dict[str, List[str]]
    embedded_assets: Dict[str, Dict[str, object]]
    tasks: List[Task]
    standalone_actions: List[Action]
    notes: List[str]
    findings: List[Finding]


def delta_to_dict(delta: ShellDelta) -> Dict[str, object]:
    """Convert a :class:`ShellDelta` into JSON-friendly primitives."""

    payload: Dict[str, object] = {
        "variables": delta.variables,
        "targets": list(delta.targets),
        "scope": list(delta.scope),
        "payloads": {key: list(values) for key, values in delta.payloads.items()},
        "embedded_assets": {
            name: dict(details) for name, details in delta.embedded_assets.items()
        },
        "notes": list(delta.notes),
        "findings": [asdict(finding) for finding in delta.findings],
        "tasks": [asdict(task) for task in delta.tasks],
        "actions": [asdict(action) for action in delta.standalone_actions],
    }
    return payload


class SAPLRepl:
    """Manage execution state for the interactive SAPL shell."""

    prompt = "sapl> "
    continuation_prompt = "... "

    def __init__(
        self,
        *,
        module_loader: Optional[ModuleLoader] = None,
        plugins: Sequence[Callable[[Interpreter], None]] | None = None,
    ) -> None:
        if module_loader is None:
            module_loader = ModuleLoader([Path.cwd()])
        self._base_paths = list(module_loader.search_paths)
        self._plugins = list(plugins or [])
        self.interpreter = self._fresh_interpreter()

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset interpreter state while keeping the configured plugins."""

        self.interpreter = self._fresh_interpreter()

    def load_script(self, path: Path) -> ShellDelta:
        """Execute the contents of *path* inside the current shell."""

        source = path.read_text(encoding="utf-8")
        delta = self.execute_snippet(source)
        # Ensure the module loader is aware of the new script directory.
        self.interpreter.module_loader.add_path(path.parent)
        return delta

    # ------------------------------------------------------------------
    # Execution primitives
    # ------------------------------------------------------------------

    def execute_snippet(self, source: str) -> ShellDelta:
        """Execute *source* code and return the resulting delta."""

        tokens = lex(source)
        program = parse(tokens)
        before = self._snapshot()
        self.interpreter.execute(program)
        return self._compute_delta(before)

    # ------------------------------------------------------------------
    # Rendering utilities
    # ------------------------------------------------------------------

    def render_delta(self, delta: ShellDelta) -> str:
        """Render a state delta as human-readable text."""

        lines: List[str] = []
        if delta.variables:
            lines.append("Variables updated:")
            for name, value in sorted(delta.variables.items()):
                lines.append(f"  {name} = {self._format_value(value)}")
        if delta.targets:
            lines.append("Targets extended:")
            for target in delta.targets:
                lines.append(f"  - {target}")
        if delta.scope:
            lines.append("Scope entries:")
            for entry in delta.scope:
                lines.append(f"  - {entry}")
        if delta.payloads:
            lines.append("Payload libraries:")
            for name, payloads in sorted(delta.payloads.items()):
                rendered = ", ".join(payloads)
                lines.append(f"  {name}: {rendered}")
        if delta.embedded_assets:
            lines.append("Embedded assets registered:")
            for name, asset in sorted(delta.embedded_assets.items()):
                language = asset.get("language", "unknown")
                metadata = asset.get("metadata") or {}
                line = f"  - {name} [{language}]"
                if metadata:
                    line += f" meta={metadata}"
                content = asset.get("content")
                if isinstance(content, bytes):
                    preview = content.decode("utf-8", "replace").strip()
                else:
                    preview = str(content).strip()
                if preview:
                    line += f" => {preview[:60]}{'…' if len(preview) > 60 else ''}"
                lines.append(line)
        if delta.tasks:
            lines.append("Tasks added:")
            for task in delta.tasks:
                heading = f"  - {task.name}"
                if task.docstring:
                    heading += f" — {task.docstring}"
                lines.append(heading)
                for action in task.steps:
                    lines.append(
                        f"      * [{action.kind}] {action.summary}"
                    )
        if delta.standalone_actions:
            lines.append("Recorded actions:")
            for action in delta.standalone_actions:
                lines.append(f"  - [{action.kind}] {action.summary}")
        if delta.notes:
            lines.append("Notes:")
            for note in delta.notes:
                lines.append(f"  - {note}")
        if delta.findings:
            lines.append("Findings:")
            for finding in delta.findings:
                lines.append(f"  - ({finding.severity}) {finding.message}")
        return "\n".join(lines)

    def render_state(self) -> str:
        """Render the interpreter context for inspection."""

        state = self.interpreter.context.format_context()
        if not state:
            return "<no variables>"
        lines = ["Current state:"]
        for name in sorted(state):
            lines.append(f"  {name} = {self._format_value(state[name])}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Interactive loop
    # ------------------------------------------------------------------

    def run_interactive(self, *, writer: Callable[[str], None] = print) -> None:
        """Launch the interactive shell loop."""

        writer("SAPL interactive shell. Type :help for assistance.")
        buffer: List[str] = []
        while True:
            try:
                line = input(self.prompt if not buffer else self.continuation_prompt)
            except EOFError:
                writer("")
                break
            except KeyboardInterrupt:
                writer("\nKeyboard interrupt — type :exit to quit.")
                buffer.clear()
                continue
            stripped = line.strip()
            if stripped.startswith(":"):
                if stripped in {":exit", ":quit"}:
                    writer("Exiting shell.")
                    break
                if stripped == ":reset":
                    self.reset()
                    writer("Interpreter state cleared.")
                    continue
                if stripped.startswith(":load"):
                    path_text = stripped[5:].strip()
                    if not path_text:
                        writer("Usage: :load <path>")
                        continue
                    target = Path(path_text).expanduser()
                    if not target.exists():
                        writer(f"File not found: {target}")
                        continue
                    try:
                        delta = self.load_script(target)
                    except SAPLError as exc:  # pragma: no cover - interactive convenience
                        writer(f"Error loading {target}: {exc}")
                        continue
                    rendered = self.render_delta(delta)
                    if rendered:
                        writer(rendered)
                    writer(f"Loaded {target}")
                    continue
                if stripped == ":run":
                    if not buffer:
                        writer("Nothing to run.")
                        continue
                    source = "\n".join(buffer)
                    buffer.clear()
                    self._execute_and_render(source, writer)
                    continue
                if stripped == ":state":
                    writer(self.render_state())
                    continue
                if stripped == ":help":
                    writer(
                        "Available commands: :help, :run, :reset, :state, :load <path>, :exit"
                    )
                    writer("Enter a blank line to execute the current buffer.")
                    continue
                writer(f"Unknown command: {stripped}")
                continue
            if stripped == "" and buffer:
                source = "\n".join(buffer)
                buffer.clear()
                self._execute_and_render(source, writer)
                continue
            if stripped == "" and not buffer:
                continue
            buffer.append(line)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fresh_interpreter(self) -> Interpreter:
        loader = ModuleLoader(self._base_paths)
        interpreter = Interpreter(module_loader=loader, plugins=self._plugins)
        return interpreter

    def _execute_and_render(self, source: str, writer: Callable[[str], None]) -> None:
        try:
            delta = self.execute_snippet(source)
        except SAPLError as exc:  # pragma: no cover - interactive convenience
            writer(f"Execution error: {exc}")
            return
        rendered = self.render_delta(delta)
        if rendered:
            writer(rendered)
        else:
            writer("No observable changes.")

    def _snapshot(self) -> Dict[str, object]:
        context = self.interpreter.context
        return {
            "variables": dict(context.format_context()),
            "targets": list(context.targets),
            "scope": list(context.scope),
            "payloads": {name: list(values) for name, values in context.payloads.items()},
            "embedded_assets": {
                name: dict(asset) for name, asset in context.embedded_assets.items()
            },
            "tasks": len(context.tasks),
            "actions": len(context.standalone_actions),
            "notes": len(context.notes),
            "findings": len(context.findings),
        }

    def _compute_delta(self, before: Dict[str, object]) -> ShellDelta:
        context = self.interpreter.context
        current_variables = context.format_context()
        previous_variables: Dict[str, object] = before.get("variables", {})  # type: ignore[assignment]
        variables: Dict[str, object] = {}
        for name, value in current_variables.items():
            if previous_variables.get(name) != value:
                variables[name] = value
        previous_targets = before.get("targets", [])  # type: ignore[assignment]
        previous_scope = before.get("scope", [])  # type: ignore[assignment]
        new_targets = context.targets[len(previous_targets) :]
        new_scope = context.scope[len(previous_scope) :]
        previous_payloads: Dict[str, List[str]] = before.get("payloads", {})  # type: ignore[assignment]
        new_payloads: Dict[str, List[str]] = {}
        for name, values in context.payloads.items():
            if previous_payloads.get(name) != values:
                new_payloads[name] = list(values)
        previous_embeds: Dict[str, Dict[str, object]] = before.get("embedded_assets", {})  # type: ignore[assignment]
        new_embeds: Dict[str, Dict[str, object]] = {}
        for name, asset in context.embedded_assets.items():
            if previous_embeds.get(name) != asset:
                new_embeds[name] = dict(asset)
        previous_tasks = before.get("tasks", 0)
        previous_actions = before.get("actions", 0)
        previous_notes = before.get("notes", 0)
        previous_findings = before.get("findings", 0)
        new_tasks = context.tasks[previous_tasks:]
        new_actions = context.standalone_actions[previous_actions:]
        new_notes = context.notes[previous_notes:]
        new_findings = context.findings[previous_findings:]
        return ShellDelta(
            variables=variables,
            targets=list(new_targets),
            scope=list(new_scope),
            payloads=new_payloads,
            embedded_assets=new_embeds,
            tasks=list(new_tasks),
            standalone_actions=list(new_actions),
            notes=list(new_notes),
            findings=list(new_findings),
        )

    def _format_value(self, value: object) -> str:
        try:
            return json.dumps(value, default=str)
        except TypeError:
            return repr(value)


__all__ = ["SAPLRepl", "ShellDelta", "delta_to_dict"]
