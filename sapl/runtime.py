"""Runtime execution for SAPL programs."""

from __future__ import annotations

import asyncio
import base64
import inspect
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

from pathlib import Path
from types import ModuleType

from . import nodes
from .errors import RuntimeError
from . import stdlib
from .lexer import lex
from .module_loader import ModuleLoader, ModuleSpec
from .parser import parse


@dataclass
class Action:
    """Represents an actionable step in a plan."""

    kind: str
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)
    line: int = 0


@dataclass
class Task:
    """A collection of related actions under a named activity."""

    name: str
    line: int
    docstring: Optional[str] = None
    steps: List[Action] = field(default_factory=list)


@dataclass
class Finding:
    """Structured representation of a potential security finding."""

    severity: str
    message: str
    line: int


@dataclass
class ExecutionResult:
    """Holds the outcome of evaluating a SAPL program."""

    targets: List[str]
    scope: List[str]
    variables: Dict[str, Any]
    payloads: Dict[str, List[str]]
    embedded_assets: Dict[str, Dict[str, Any]]
    tasks: List[Task]
    standalone_actions: List[Action]
    notes: List[str]
    findings: List[Finding]
    report_destination: Optional[str]


class _BreakSignal(Exception):
    pass


class _ContinueSignal(Exception):
    pass


class _ReturnSignal(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value


@dataclass
class ExecutionContext:
    """State maintained while executing a SAPL program."""

    def __init__(self) -> None:
        self.variables: Dict[str, Any] = {}
        self.frames: List[Dict[str, Any]] = [self.variables]
        self.modules: Dict[str, Any] = {}
        self.targets: List[str] = []
        self.scope: List[str] = []
        self.payloads: Dict[str, List[str]] = {}
        self.embedded_assets: Dict[str, Dict[str, Any]] = {}
        self.tasks: List[Task] = []
        self.standalone_actions: List[Action] = []
        self.notes: List[str] = []
        self.findings: List[Finding] = []
        self.report_destination: Optional[str] = None
        self._task_stack: List[Task] = []
        self.builtins: Dict[str, Any] = stdlib.load_builtins()

    @property
    def current_task(self) -> Optional[Task]:
        return self._task_stack[-1] if self._task_stack else None

    @contextmanager
    def push_task(self, task: Task):
        self._task_stack.append(task)
        try:
            yield
        finally:
            self._task_stack.pop()

    def push_frame(self, frame: Optional[Dict[str, Any]] = None) -> None:
        if frame is None:
            frame = {}
        self.frames.append(frame)

    def pop_frame(self) -> None:
        if len(self.frames) <= 1:
            raise RuntimeError("Cannot pop global frame")
        self.frames.pop()

    def add_action(self, action: Action) -> None:
        if self.current_task is not None:
            self.current_task.steps.append(action)
        else:
            self.standalone_actions.append(action)

    def format_context(self) -> Dict[str, Any]:
        rendered: Dict[str, Any] = {}
        for name, value in self.variables.items():
            if callable(value):
                continue
            rendered[name] = value
        rendered.setdefault("targets", self.targets)
        rendered.setdefault("scope", self.scope)
        if self.targets:
            rendered.setdefault("target", self.targets[0])
        for name, values in self.payloads.items():
            rendered.setdefault(f"payload_{name}", values)
        for name, asset in self.embedded_assets.items():
            content = asset.get("content")
            if isinstance(content, bytes):
                rendered.setdefault(f"embed_{name}", content.decode("utf-8", "replace"))
            else:
                rendered.setdefault(f"embed_{name}", content)
            metadata = asset.get("metadata")
            if metadata is not None:
                rendered.setdefault(f"embed_{name}_meta", metadata)
        return rendered


class SAPLFunction:
    """User-defined function implemented in SAPL."""

    def __init__(
        self,
        interpreter: "Interpreter",
        name: str,
        parameters: List[nodes.Parameter],
        body: Iterable[nodes.Statement],
        defaults: Dict[str, Any],
        closure: Dict[str, Any],
        docstring: Optional[str] = None,
        *,
        is_async: bool = False,
    ) -> None:
        self.interpreter = interpreter
        self.name = name
        self.parameters = parameters
        self.body = list(body)
        self.defaults = defaults
        self.closure = closure
        self.docstring = docstring
        self.__doc__ = docstring
        self.is_async = is_async

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.interpreter._invoke_function(self, list(args), dict(kwargs))

    def bind_to_class(self) -> Any:
        def method(instance: Any, *args: Any, **kwargs: Any) -> Any:
            return self.interpreter._invoke_function(
                self,
                list(args),
                dict(kwargs),
                bound_instance=instance,
            )

        method.__name__ = self.name
        method.__qualname__ = self.name
        method.__doc__ = self.docstring
        return method


@dataclass
class PendingAsyncCall:
    """Deferred invocation for asynchronous SAPL functions."""

    interpreter: "Interpreter"
    function: SAPLFunction
    args: List[Any]
    kwargs: Dict[str, Any]
    bound_instance: Any | None = None

    def resolve(self) -> Any:
        return self.interpreter._call_function(
            self.function,
            list(self.args),
            dict(self.kwargs),
            bound_instance=self.bound_instance,
            asynchronous=True,
        )


class SAPLLambda:
    """Callable representing a lambda expression."""

    def __init__(
        self,
        interpreter: "Interpreter",
        parameters: List[nodes.Parameter],
        body: nodes.Expression,
        defaults: Dict[str, Any],
        closure: Dict[str, Any],
        line: int,
    ) -> None:
        self.interpreter = interpreter
        self.parameters = parameters
        self.body = body
        self.defaults = defaults
        self.closure = closure
        self.line = line

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        frame = dict(self.closure)
        remaining_args = list(args)
        remaining_kwargs = dict(kwargs)
        for param in self.parameters:
            if remaining_args:
                frame[param.name] = remaining_args.pop(0)
            elif param.name in remaining_kwargs:
                frame[param.name] = remaining_kwargs.pop(param.name)
            elif param.name in self.defaults:
                frame[param.name] = self.defaults[param.name]
            else:
                raise RuntimeError(
                    f"Missing value for parameter '{param.name}' in lambda defined on line {self.line}"
                )
        if remaining_args or remaining_kwargs:
            raise RuntimeError(
                f"Too many arguments supplied to lambda defined on line {self.line}"
            )
        self.interpreter.context.push_frame(frame)
        try:
            return self.interpreter._evaluate_expression(self.body, self.line)
        finally:
            self.interpreter.context.pop_frame()

class Interpreter:
    """Executes SAPL programs and returns a structured plan."""

    def __init__(
        self,
        *,
        module_loader: ModuleLoader | None = None,
        plugins: Sequence[Callable[["Interpreter"], None]] | None = None,
    ) -> None:
        self.context = ExecutionContext()
        self._function_stack: List[SAPLFunction] = []
        if module_loader is None:
            module_loader = ModuleLoader([Path.cwd()])
        self.module_loader = module_loader
        self._applied_plugins: List[str] = []
        if plugins:
            for plugin in plugins:
                self.register_plugin(plugin)

    def execute(self, program: nodes.Program) -> ExecutionResult:
        for statement in program.statements:
            self._execute_statement(statement)
        return ExecutionResult(
            targets=list(self.context.targets),
            scope=list(self.context.scope),
            variables=self._snapshot_variables(),
            payloads={key: list(value) for key, value in self.context.payloads.items()},
            embedded_assets={
                name: {
                    "language": asset.get("language"),
                    "content": asset.get("content"),
                    "metadata": dict(asset.get("metadata", {})),
                }
                for name, asset in self.context.embedded_assets.items()
            },
            tasks=list(self.context.tasks),
            standalone_actions=list(self.context.standalone_actions),
            notes=list(self.context.notes),
            findings=list(self.context.findings),
            report_destination=self.context.report_destination,
        )

    def register_builtin(self, name: str, value: Any) -> None:
        """Expose *value* to SAPL programs under *name*."""

        self.context.builtins[name] = value

    def register_plugin(self, plugin: Callable[["Interpreter"], None]) -> None:
        """Apply *plugin* to this interpreter instance."""

        plugin(self)
        name = getattr(plugin, "__sapl_plugin_name__", getattr(plugin, "__name__", "plugin"))
        self._applied_plugins.append(str(name))

    @property
    def active_plugins(self) -> List[str]:
        """Return the plugin identifiers applied to this interpreter."""

        return list(self._applied_plugins)

    # Statement execution ----------------------------------------------

    def _execute_statement(self, statement: nodes.Statement) -> None:
        if isinstance(statement, nodes.SetStatement):
            value = self._evaluate_expression(statement.value, statement.line)
            self.context.variables[statement.name] = value
            self.context.frames[0][statement.name] = value
            return
        if isinstance(statement, nodes.TargetStatement):
            for value in self._coerce_iterable(statement.value, statement.line):
                self.context.targets.append(str(value))
            return
        if isinstance(statement, nodes.ScopeStatement):
            values = self._coerce_iterable(statement.value, statement.line)
            self.context.scope.extend(str(item) for item in values)
            return
        if isinstance(statement, nodes.PayloadStatement):
            payload_values = [str(item) for item in self._coerce_iterable(statement.value, statement.line)]
            self.context.payloads[statement.name] = payload_values
            return
        if isinstance(statement, nodes.EmbedStatement):
            language = str(statement.language).lower()
            content_value = self._evaluate_expression(statement.content, statement.line)
            metadata_value: Dict[str, Any] = {}
            if statement.metadata is not None:
                metadata_object = self._evaluate_expression(statement.metadata, statement.line)
                if metadata_object is None:
                    metadata_value = {}
                elif isinstance(metadata_object, dict):
                    metadata_value = dict(metadata_object)
                else:
                    raise RuntimeError("EMBED metadata must evaluate to a dictionary")
            if isinstance(content_value, str):
                stored_content: Any = self._interpolate(content_value)
                original_length = len(stored_content)
            elif isinstance(content_value, bytes):
                original_length = len(content_value)
                stored_content = base64.b64encode(content_value).decode("ascii")
                metadata_value = dict(metadata_value)
                metadata_value.setdefault("content_encoding", "base64")
            else:
                raise RuntimeError("EMBED content must evaluate to str or bytes")
            asset = {
                "language": language,
                "content": stored_content,
                "metadata": metadata_value,
            }
            self.context.embedded_assets[statement.name] = asset
            preview_source = str(stored_content)
            details = {
                "language": language,
                "metadata": metadata_value,
                "length": original_length,
            }
            if isinstance(content_value, bytes):
                details["encoding"] = "base64"
            preview = preview_source.strip()
            if preview:
                details["preview"] = (preview[:80] + "…") if len(preview) > 80 else preview
            self.context.add_action(
                Action(
                    kind="embed",
                    summary=f"Embed {statement.name} ({language})",
                    details=details,
                    line=statement.line,
                )
            )
            return
        if isinstance(statement, nodes.TaskStatement):
            task_name = self._interpolate(statement.name)
            task = Task(task_name, statement.line, docstring=statement.docstring)
            self.context.tasks.append(task)
            with self.context.push_task(task):
                self._execute_block(statement.body)
            return
        if isinstance(statement, nodes.PortScanStatement):
            ports = [str(item) for item in self._coerce_iterable(statement.ports, statement.line)]
            tool = self._evaluate_string(statement.tool, statement.line) if statement.tool else None
            summary = f"Port scan ports {', '.join(ports)}"
            action = Action(
                kind="portscan",
                summary=summary,
                details={"ports": ports, "tool": tool},
                line=statement.line,
            )
            self.context.add_action(action)
            return
        if isinstance(statement, nodes.HttpRequestStatement):
            target = self._evaluate_string(statement.target, statement.line)
            summary = f"HTTP {statement.method} {target}"
            details = {
                "method": statement.method,
                "target": target,
            }
            if statement.expect_status is not None:
                details["expect_status"] = statement.expect_status
            if statement.contains is not None:
                details["contains"] = self._evaluate_string(statement.contains, statement.line)
            action = Action(kind="http", summary=summary, details=details, line=statement.line)
            self.context.add_action(action)
            return
        if isinstance(statement, nodes.FuzzStatement):
            resource = self._evaluate_string(statement.resource, statement.line)
            method = statement.method or "GET"
            payloads: List[str] = []
            if statement.payload is not None:
                if statement.payload not in self.context.payloads:
                    raise RuntimeError(f"Unknown payload: {statement.payload}")
                payloads.extend(self.context.payloads[statement.payload])
            if statement.payloads_expr is not None:
                payloads.extend(str(item) for item in self._coerce_iterable(statement.payloads_expr, statement.line))
            action = Action(
                kind="fuzz",
                summary=f"Fuzz {resource} using {len(payloads) or 'custom'} payloads",
                details={"resource": resource, "method": method, "payloads": payloads},
                line=statement.line,
            )
            self.context.add_action(action)
            return
        if isinstance(statement, nodes.NoteStatement):
            message = self._evaluate_string(statement.message, statement.line)
            self.context.notes.append(message)
            return
        if isinstance(statement, nodes.FindingStatement):
            message = self._evaluate_string(statement.message, statement.line)
            finding = Finding(statement.severity, message, statement.line)
            self.context.findings.append(finding)
            return
        if isinstance(statement, nodes.RunStatement):
            command = self._evaluate_string(statement.command, statement.line)
            details = {"command": command}
            if statement.save_as:
                details["save_as"] = statement.save_as
            action = Action(kind="run", summary=f"Run command: {command}", details=details, line=statement.line)
            self.context.add_action(action)
            return
        if isinstance(statement, nodes.ReportStatement):
            destination = self._evaluate_string(statement.destination, statement.line)
            self.context.report_destination = destination
            return
        if isinstance(statement, nodes.InputStatement):
            input_fn = self.context.builtins.get("input")
            if input_fn is None:
                raise RuntimeError("INPUT statements require the 'input' builtin")
            prompt = ""
            if statement.prompt is not None:
                prompt_value = self._evaluate_expression(statement.prompt, statement.line)
                if isinstance(prompt_value, str):
                    prompt = self._interpolate(prompt_value)
                else:
                    prompt = str(prompt_value)
            value = input_fn(prompt)
            if statement.target is not None:
                self._assign(statement.target, value, statement.line)
            summary = f"Input {statement.target or 'value'}"
            details = {"prompt": prompt, "value": value}
            self.context.add_action(Action(kind="input", summary=summary, details=details, line=statement.line))
            return
        if isinstance(statement, nodes.OutputStatement):
            output_fn = self.context.builtins.get("print")
            if output_fn is None:
                raise RuntimeError("OUTPUT statements require the 'print' builtin")
            rendered = self._evaluate_expression(statement.value, statement.line)
            if isinstance(rendered, str):
                rendered = self._interpolate(rendered)
            output_fn(rendered)
            summary = f"Output {rendered}"
            details = {"value": rendered}
            self.context.add_action(Action(kind="output", summary=summary, details=details, line=statement.line))
            return
        if isinstance(statement, nodes.ForStatement):
            iterable = self._evaluate_expression(statement.iterable, statement.line)
            previous_value = self._lookup_variable(statement.iterator)
            sentinel = object()
            if previous_value is None:
                previous_value = sentinel
            try:
                for item in self._iterable(iterable, statement.line):
                    self._assign(statement.iterator, item, statement.line)
                    try:
                        self._execute_block(statement.body)
                    except _ContinueSignal:
                        continue
            except _BreakSignal:
                pass
            finally:
                if previous_value is sentinel:
                    self._delete(statement.iterator)
                else:
                    self._assign(statement.iterator, previous_value, statement.line)
            return
        if isinstance(statement, nodes.IfStatement):
            if self._truthy(self._evaluate_expression(statement.condition, statement.line)):
                self._execute_block(statement.body)
            else:
                handled = False
                for expr, body in statement.elif_blocks:
                    if self._truthy(self._evaluate_expression(expr, statement.line)):
                        self._execute_block(body)
                        handled = True
                        break
                if not handled and statement.else_body:
                    self._execute_block(statement.else_body)
            return
        if isinstance(statement, nodes.WhileStatement):
            try:
                while self._truthy(self._evaluate_expression(statement.condition, statement.line)):
                    try:
                        self._execute_block(statement.body)
                    except _ContinueSignal:
                        continue
            except _BreakSignal:
                pass
            else:
                if statement.else_body:
                    self._execute_block(statement.else_body)
            return
        if isinstance(statement, nodes.BreakStatement):
            raise _BreakSignal()
        if isinstance(statement, nodes.ContinueStatement):
            raise _ContinueSignal()
        if isinstance(statement, nodes.PassStatement):
            return
        if isinstance(statement, nodes.ReturnStatement):
            if not self._function_stack:
                raise RuntimeError("RETURN used outside of a function")
            value = self._evaluate_expression(statement.value, statement.line) if statement.value is not None else None
            raise _ReturnSignal(value)
        if isinstance(statement, nodes.FunctionDefinition):
            defaults = {}
            for param in statement.parameters:
                if param.default is not None:
                    defaults[param.name] = self._evaluate_expression(param.default, statement.line)
            closure: Dict[str, Any] = {}
            for frame in self.context.frames:
                closure.update(frame)
            function = SAPLFunction(
                self,
                statement.name,
                statement.parameters,
                statement.body,
                defaults,
                closure,
                statement.docstring,
                is_async=statement.is_async,
            )
            target_frame = self.context.frames[-1]
            target_frame[statement.name] = function
            if target_frame is self.context.frames[0]:
                self.context.variables[statement.name] = function
            return
        if isinstance(statement, nodes.ExpressionStatement):
            self._evaluate_expression(statement.expression, statement.line)
            return
        if isinstance(statement, nodes.AssignmentStatement):
            value = self._evaluate_expression(statement.value, statement.line)
            targets = [self._materialise_target(target, statement.line) for target in statement.targets]
            if len(targets) == 1:
                self._assign_target(targets[0], value, statement.line)
            else:
                values = list(self._iterable(value, statement.line))
                if len(values) != len(targets):
                    raise RuntimeError("Mismatched assignment value count")
                for target, individual in zip(targets, values):
                    self._assign_target(target, individual, statement.line)
            return
        if isinstance(statement, nodes.AugmentedAssignmentStatement):
            target = self._materialise_target(statement.target, statement.line)
            current = self._read_target(target, statement.line)
            increment = self._evaluate_expression(statement.value, statement.line)
            result = self._apply_augmented(statement.operator, current, increment, statement.line)
            self._assign_target(target, result, statement.line)
            return
        if isinstance(statement, nodes.WithStatement):
            with ExitStack() as stack:
                self.context.push_frame({})
                try:
                    for item in statement.items:
                        manager = self._evaluate_expression(item.context, statement.line)
                        entered = stack.enter_context(manager)
                        if item.alias:
                            self._assign(item.alias, entered, statement.line)
                    self._execute_block(statement.body)
                finally:
                    self.context.pop_frame()
            return
        if isinstance(statement, nodes.TryStatement):
            try:
                self._execute_block(statement.body)
            except Exception as exc:  # pylint: disable=broad-except
                handled = False
                for handler in statement.handlers:
                    if handler.exception_type is not None:
                        expected = self._evaluate_expression(handler.exception_type, statement.line)
                        expected_types = expected if isinstance(expected, tuple) else (expected,)
                        if not any(isinstance(exc, typ) for typ in expected_types if isinstance(typ, type)):
                            continue
                    self.context.push_frame({})
                    try:
                        if handler.alias:
                            self._assign(handler.alias, exc, statement.line)
                        self._execute_block(handler.body)
                    finally:
                        self.context.pop_frame()
                    handled = True
                    break
                if not handled:
                    raise
            else:
                if statement.else_body:
                    self._execute_block(statement.else_body)
            finally:
                if statement.finally_body:
                    self._execute_block(statement.finally_body)
            return
        if isinstance(statement, nodes.RaiseStatement):
            if statement.value is None:
                raise RuntimeError("RAISE requires an exception value")
            value = self._evaluate_expression(statement.value, statement.line)
            if isinstance(value, BaseException):
                raise value
            raise RuntimeError(f"Cannot raise value of type {type(value).__name__}")
        if isinstance(statement, nodes.ImportStatement):
            for item in statement.items:
                module = self._import_module(item.module)
                alias = item.alias or item.module[-1]
                self.context.variables[alias] = module
                self.context.frames[0][alias] = module
                self.context.modules[alias] = module
            return
        if isinstance(statement, nodes.FromImportStatement):
            module = self._import_module(statement.module)
            for item in statement.items:
                if item.name == "*":
                    for attr in stdlib.module_public_names(module):
                        value = getattr(module, attr)
                        self.context.variables[attr] = value
                        self.context.frames[0][attr] = value
                    continue
                if not hasattr(module, item.name):
                    raise RuntimeError(f"Module '{'.'.join(statement.module)}' has no attribute '{item.name}'")
                alias = item.alias or item.name
                value = getattr(module, item.name)
                self.context.variables[alias] = value
                self.context.frames[0][alias] = value
            return
        if isinstance(statement, nodes.ClassDefinition):
            bases = [self._evaluate_expression(expr, statement.line) for expr in statement.bases]
            if not bases:
                bases = [object]
            class_namespace: Dict[str, Any] = {}
            self.context.push_frame(class_namespace)
            try:
                self._execute_block(statement.body)
            finally:
                self.context.pop_frame()
            attrs: Dict[str, Any] = {}
            for key, value in class_namespace.items():
                if isinstance(value, SAPLFunction):
                    attrs[key] = value.bind_to_class()
                else:
                    attrs[key] = value
            if statement.docstring is not None:
                attrs.setdefault("__doc__", statement.docstring)
            cls = type(statement.name, tuple(bases), attrs)
            self.context.variables[statement.name] = cls
            self.context.frames[0][statement.name] = cls
            return
        raise RuntimeError(f"Unsupported statement type: {type(statement)!r}")

    def _import_module(self, module_path: List[str]) -> ModuleType:
        dotted = ".".join(module_path)
        if dotted in self.context.modules:
            cached = self.context.modules[dotted]
            if isinstance(cached, ModuleType):
                return cached
        try:
            module = stdlib.import_module(module_path)
        except RuntimeError as exc:
            spec: ModuleSpec | None = None
            if "not part of the SAPL standard library" in str(exc):
                spec = self.module_loader.resolve(module_path)
            if spec is None:
                raise
            module = self._load_custom_module(spec)
        self.context.modules[dotted] = module
        return module

    def _load_custom_module(self, spec: ModuleSpec) -> ModuleType:
        source = spec.path.read_text(encoding="utf-8")
        program = parse(lex(source))
        child_loader = self.module_loader.spawn_child(spec.path.parent)
        sub_interpreter = type(self)(module_loader=child_loader)
        sub_interpreter.execute(program)
        namespace = dict(sub_interpreter.context.variables)
        module = ModuleType(spec.dotted)
        module.__dict__.update(namespace)
        module.__file__ = str(spec.path)
        if spec.kind == "package":
            module.__path__ = [str(spec.path.parent)]
        module.__package__ = spec.dotted.rpartition(".")[0]
        module.__sapl_exports__ = sorted(namespace.keys())
        self.module_loader.add_path(spec.path.parent)
        self.context.modules[spec.dotted] = module
        return module

    def _execute_block(self, statements: Iterable[nodes.Statement]) -> None:
        for statement in statements:
            self._execute_statement(statement)

    # Function invocation ----------------------------------------------

    def _invoke_function(
        self,
        function: SAPLFunction,
        args: List[Any],
        kwargs: Dict[str, Any],
        *,
        bound_instance: Any | None = None,
    ) -> Any:
        if function.is_async:
            return PendingAsyncCall(self, function, args, kwargs, bound_instance)
        return self._call_function(function, args, kwargs, bound_instance=bound_instance)

    def _call_function(
        self,
        function: SAPLFunction,
        args: List[Any],
        kwargs: Dict[str, Any],
        *,
        bound_instance: Any | None = None,
        asynchronous: bool = False,
    ) -> Any:
        if function.is_async and not asynchronous:
            raise RuntimeError(f"Function '{function.name}' is asynchronous and must be awaited")
        frame = dict(function.closure)
        parameters = list(function.parameters)
        if bound_instance is not None:
            if not parameters:
                raise RuntimeError(f"Function '{function.name}' does not accept arguments")
            first_param = parameters[0]
            frame[first_param.name] = bound_instance
            parameters = parameters[1:]
        remaining_args = list(args)
        remaining_kwargs = dict(kwargs)
        for param in parameters:
            if remaining_args:
                frame[param.name] = remaining_args.pop(0)
            elif param.name in remaining_kwargs:
                frame[param.name] = remaining_kwargs.pop(param.name)
            elif param.name in function.defaults:
                frame[param.name] = function.defaults[param.name]
            else:
                raise RuntimeError(f"Missing value for parameter '{param.name}' in function '{function.name}'")
        if remaining_args or remaining_kwargs:
            raise RuntimeError(f"Too many arguments supplied to function '{function.name}'")
        self.context.push_frame(frame)
        self._function_stack.append(function)
        try:
            self._execute_block(function.body)
        except _ReturnSignal as signal:
            return signal.value
        finally:
            self._function_stack.pop()
            self.context.pop_frame()
        return None

    # Expression evaluation -------------------------------------------

    def _evaluate_expression(self, expression: nodes.Expression, line: int) -> Any:
        if isinstance(expression, nodes.Identifier):
            return self._resolve_identifier(expression.name, line)
        if isinstance(expression, nodes.AttributeReference):
            value = self._evaluate_expression(expression.value, line)
            if hasattr(value, expression.attribute):
                attr = getattr(value, expression.attribute)
                if isinstance(attr, SAPLFunction):
                    return attr
                return attr
            if isinstance(value, dict) and expression.attribute in value:
                return value[expression.attribute]
            raise RuntimeError(f"Object of type {type(value).__name__} has no attribute '{expression.attribute}'")
        if isinstance(expression, nodes.IndexReference):
            value = self._evaluate_expression(expression.value, line)
            index = self._evaluate_expression(expression.index, line)
            try:
                return value[index]
            except Exception as exc:  # pylint: disable=broad-except
                raise RuntimeError(f"Index error: {exc}") from exc
        if isinstance(expression, nodes.CallExpression):
            function = self._evaluate_expression(expression.function, line)
            args = [self._evaluate_expression(arg, line) for arg in expression.args]
            kwargs = {key: self._evaluate_expression(value, line) for key, value in expression.kwargs.items()}
            if isinstance(function, SAPLFunction):
                return function(*args, **kwargs)
            if callable(function):
                return function(*args, **kwargs)
            raise RuntimeError(f"Attempted to call non-callable object of type {type(function).__name__}")
        if isinstance(expression, nodes.UnaryExpression):
            operand = self._evaluate_expression(expression.operand, line)
            if expression.operator == "NEGATE":
                return -operand
            if expression.operator == "POSITIVE":
                return +operand
            if expression.operator == "NOT":
                return not self._truthy(operand)
            raise RuntimeError(f"Unsupported unary operator {expression.operator}")
        if isinstance(expression, nodes.BinaryExpression):
            left = self._evaluate_expression(expression.left, line)
            right = self._evaluate_expression(expression.right, line)
            return self._apply_operator(expression.operator, left, right, line)
        if isinstance(expression, nodes.ListExpression):
            return [self._evaluate_expression(elem, line) for elem in expression.elements]
        if isinstance(expression, nodes.TupleExpression):
            return tuple(self._evaluate_expression(elem, line) for elem in expression.elements)
        if isinstance(expression, nodes.DictExpression):
            return {self._evaluate_expression(key, line): self._evaluate_expression(value, line) for key, value in expression.entries}
        if isinstance(expression, nodes.SetExpression):
            return {self._evaluate_expression(elem, line) for elem in expression.elements}
        if isinstance(expression, nodes.ListComprehension):
            iterable = self._evaluate_expression(expression.iterable, line)
            results: List[Any] = []
            self.context.push_frame({})
            try:
                for item in self._iterable(iterable, line):
                    self._assign(expression.iterator, item, line)
                    if expression.condition is not None:
                        condition_value = self._evaluate_expression(expression.condition, line)
                        if not self._truthy(condition_value):
                            continue
                    results.append(self._evaluate_expression(expression.expression, line))
            finally:
                self.context.pop_frame()
            return results
        if isinstance(expression, nodes.ConditionalExpression):
            condition = self._evaluate_expression(expression.condition, line)
            branch = expression.if_true if self._truthy(condition) else expression.if_false
            return self._evaluate_expression(branch, line)
        if isinstance(expression, nodes.LambdaExpression):
            defaults: Dict[str, Any] = {}
            for param in expression.parameters:
                if param.default is not None:
                    defaults[param.name] = self._evaluate_expression(param.default, line)
            closure: Dict[str, Any] = {}
            for frame in self.context.frames:
                closure.update(frame)
            return SAPLLambda(self, expression.parameters, expression.body, defaults, closure, line)
        if isinstance(expression, nodes.AwaitExpression):
            value = self._evaluate_expression(expression.expression, line)
            return self._await(value, line)
        return expression

    def _evaluate_string(self, expression: nodes.Expression | None, line: int) -> str:
        if expression is None:
            return ""
        value = self._evaluate_expression(expression, line)
        if not isinstance(value, str):
            raise RuntimeError(f"Expected string value on line {line}, got {type(value).__name__}")
        return self._interpolate(value)

    # Helpers ----------------------------------------------------------

    def _snapshot_variables(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for name, value in self.context.variables.items():
            if callable(value):
                continue
            result[name] = value
        return result

    def _coerce_iterable(self, expression: nodes.Expression, line: int) -> List[Any]:
        value = self._evaluate_expression(expression, line)
        return list(self._iterable(value, line))

    def _iterable(self, value: Any, line: int) -> Iterable[Any]:
        if isinstance(value, str):
            return [value]
        try:
            return iter(value)
        except TypeError as exc:
            raise RuntimeError(f"Value of type {type(value).__name__} is not iterable on line {line}") from exc

    def _assign(self, name: str, value: Any, line: int) -> None:
        self.context.frames[-1][name] = value
        if len(self.context.frames) == 1:
            self.context.variables[name] = value

    def _assign_target(self, target: Any, value: Any, line: int) -> None:
        if isinstance(target, nodes.Identifier):
            self._assign(target.name, value, line)
        elif isinstance(target, nodes.AttributeReference):
            obj = self._evaluate_expression(target.value, line)
            setattr(obj, target.attribute, value)
        elif isinstance(target, nodes.IndexReference):
            obj = self._evaluate_expression(target.value, line)
            index = self._evaluate_expression(target.index, line)
            obj[index] = value
        else:
            raise RuntimeError("Unsupported assignment target")

    def _read_target(self, target: Any, line: int) -> Any:
        if isinstance(target, nodes.Identifier):
            return self._resolve_identifier(target.name, line)
        if isinstance(target, nodes.AttributeReference):
            obj = self._evaluate_expression(target.value, line)
            return getattr(obj, target.attribute)
        if isinstance(target, nodes.IndexReference):
            obj = self._evaluate_expression(target.value, line)
            index = self._evaluate_expression(target.index, line)
            return obj[index]
        raise RuntimeError("Unsupported assignment target")

    def _materialise_target(self, target: Any, line: int) -> Any:
        if isinstance(target, (nodes.Identifier, nodes.AttributeReference, nodes.IndexReference)):
            return target
        raise RuntimeError("Invalid assignment target")

    def _apply_operator(self, operator: str, left: Any, right: Any, line: int) -> Any:
        if operator == "PLUS":
            return left + right
        if operator == "MINUS":
            return left - right
        if operator == "STAR":
            return left * right
        if operator == "SLASH":
            return left / right
        if operator == "DBLSLASH":
            return left // right
        if operator == "PERCENT":
            return left % right
        if operator == "POWER":
            return left ** right
        if operator == "EQ":
            return left == right
        if operator == "NEQ":
            return left != right
        if operator == "LT":
            return left < right
        if operator == "LTE":
            return left <= right
        if operator == "GT":
            return left > right
        if operator == "GTE":
            return left >= right
        if operator == "AND":
            return self._truthy(left) and self._truthy(right)
        if operator == "OR":
            return self._truthy(left) or self._truthy(right)
        if operator == "IN":
            return left in right
        raise RuntimeError(f"Unsupported binary operator {operator}")

    def _apply_augmented(self, operator: str, current: Any, increment: Any, line: int) -> Any:
        mapping = {
            "PLUSEQ": ("PLUS", current, increment),
            "MINUSEQ": ("MINUS", current, increment),
            "STAREQ": ("STAR", current, increment),
            "SLASHEQ": ("SLASH", current, increment),
            "DBLSLASHEQ": ("DBLSLASH", current, increment),
            "PERCENTEQ": ("PERCENT", current, increment),
            "POWEQ": ("POWER", current, increment),
        }
        if operator not in mapping:
            raise RuntimeError(f"Unsupported augmented operator {operator}")
        op, left, right = mapping[operator]
        return self._apply_operator(op, left, right, line)

    def _truthy(self, value: Any) -> bool:
        return bool(value)

    def _await(self, value: Any, line: int) -> Any:
        if isinstance(value, PendingAsyncCall):
            return value.resolve()
        if inspect.isawaitable(value):
            try:
                return asyncio.run(value)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                previous: asyncio.AbstractEventLoop | None = None
                try:
                    try:
                        previous = asyncio.get_event_loop()
                    except RuntimeError:
                        previous = None
                    asyncio.set_event_loop(loop)
                    return loop.run_until_complete(value)
                finally:
                    loop.close()
                    asyncio.set_event_loop(previous)
        raise RuntimeError(f"AWAIT requires an awaitable value on line {line}")

    def _resolve_identifier(self, name: str, line: int) -> Any:
        for frame in reversed(self.context.frames):
            if name in frame:
                return frame[name]
        if name in self.context.variables:
            return self.context.variables[name]
        if name in self.context.modules:
            return self.context.modules[name]
        if name in self.context.payloads:
            return list(self.context.payloads[name])
        if name == "targets":
            return list(self.context.targets)
        if name == "scope":
            return list(self.context.scope)
        if name in self.context.builtins:
            return self.context.builtins[name]
        raise RuntimeError(f"Unknown identifier '{name}' referenced on line {line}")

    def _lookup_variable(self, name: str) -> Any | None:
        for frame in reversed(self.context.frames):
            if name in frame:
                return frame[name]
        return None

    def _delete(self, name: str) -> None:
        for frame in reversed(self.context.frames):
            if name in frame:
                del frame[name]
                if frame is self.context.frames[0] and name in self.context.variables:
                    del self.context.variables[name]
                return

    def _interpolate(self, value: str) -> str:
        format_map = self.context.format_context()
        return value.format_map(_FormatDict(format_map))


class _FormatDict(dict):
    """Safe dictionary for str.format_map with graceful fallback."""

    def __missing__(self, key: str) -> str:  # pragma: no cover - defensive
        return "{" + key + "}"
