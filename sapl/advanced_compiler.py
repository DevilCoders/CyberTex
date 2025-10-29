"""Advanced compiler that enriches SAPL compilation with metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from . import nodes
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
from .lexer import lex
from .parser import parse


@dataclass
class IntrospectedParameter:
    """Description of a function parameter."""

    name: str
    default: str | None = None
    kind: str = "positional"


@dataclass
class IntrospectedFunction:
    """Metadata describing a function or method in a SAPL program."""

    name: str
    parameters: List[IntrospectedParameter]
    is_async: bool
    line: int
    docstring: str | None = None


@dataclass
class IntrospectedClass:
    """Metadata describing a class definition."""

    name: str
    bases: List[str]
    methods: List[IntrospectedFunction] = field(default_factory=list)
    line: int = 0
    docstring: str | None = None


@dataclass
class AdvancedCompileArtifact:
    """Compilation output enriched with structural metadata."""

    target: str
    optimization_level: int
    metadata: Dict[str, Any]
    payload: Any

    def serialise(self) -> Dict[str, Any]:
        """Return a JSON-serialisable payload describing the compilation."""

        if hasattr(self.payload, "render"):
            payload: Any = self.payload.render()
        elif isinstance(self.payload, dict):
            payload = self.payload
        elif hasattr(self.payload, "instructions") and hasattr(self.payload, "constants"):
            payload = {
                "instructions": list(self.payload.instructions),
                "constants": list(self.payload.constants),
            }
        else:
            payload = self.payload
        return {
            "target": self.target,
            "optimization_level": self.optimization_level,
            "metadata": self.metadata,
            "payload": payload,
        }

    def pretty(self) -> str:
        """Produce a human-readable representation of the artifact."""

        lines: List[str] = [
            f"Target: {self.target}",
            f"Optimization level: {self.optimization_level}",
        ]
        imports = self.metadata.get("imports", [])
        lines.append("Imports: " + (", ".join(imports) if imports else "<none>"))
        if self.metadata.get("functions"):
            lines.append("Functions:")
            for func in self.metadata["functions"]:
                param_text = ", ".join(
                    f"{param['name']}={param['default']}"
                    if param.get("default")
                    else param["name"]
                    for param in func["parameters"]
                )
                signature = param_text or "<no parameters>"
                async_prefix = "async " if func.get("is_async") else ""
                lines.append(
                    f"  - {async_prefix}{func['name']}({signature}) @ line {func['line']}"
                )
        if self.metadata.get("classes"):
            lines.append("Classes:")
            for cls in self.metadata["classes"]:
                bases = ", ".join(cls["bases"]) or "object"
                lines.append(f"  - {cls['name']}({bases}) @ line {cls['line']}")
                for method in cls.get("methods", []):
                    param_text = ", ".join(
                        f"{param['name']}={param['default']}"
                        if param.get("default")
                        else param["name"]
                        for param in method["parameters"]
                    )
                    signature = param_text or "<no parameters>"
                    async_prefix = "async " if method.get("is_async") else ""
                    lines.append(f"      * {async_prefix}{method['name']}({signature})")
        if self.metadata.get("tasks"):
            lines.append("Tasks: " + ", ".join(self.metadata["tasks"]))
        if self.metadata.get("payloads"):
            lines.append("Payloads: " + ", ".join(self.metadata["payloads"]))
        payload_repr = self.serialise()["payload"]
        lines.append("\nCompiled payload:\n" + str(payload_repr))
        return "\n".join(lines)


class AdvancedCompiler:
    """Front-end that exposes compilation metadata and multiple backends."""

    def __init__(self, optimization_level: int = 1) -> None:
        self.optimization_level = optimization_level

    def compile_path(self, path: Path, *, target: str = "machine") -> AdvancedCompileArtifact:
        source = path.read_text(encoding="utf-8")
        program = parse(lex(source))
        return self._compile(program, target=target, module_name=path.stem)

    def compile_source(
        self,
        source: str,
        *,
        target: str = "machine",
        module_name: str = "__main__",
    ) -> AdvancedCompileArtifact:
        program = parse(lex(source))
        return self._compile(program, target=target, module_name=module_name)

    # ------------------------------------------------------------------
    def _compile(
        self,
        program: nodes.Program,
        *,
        target: str,
        module_name: str,
    ) -> AdvancedCompileArtifact:
        metadata = self._introspect(program, module_name=module_name)
        payload = self._emit(program, target=target)
        return AdvancedCompileArtifact(
            target=target,
            optimization_level=self.optimization_level,
            metadata=metadata,
            payload=payload,
        )

    def _emit(self, program: nodes.Program, *, target: str) -> Any:
        if target == "machine":
            return MachineCodeCompiler().compile(program)
        if target == "bytecode":
            return BytecodeCompiler().compile(program)
        if target == "python":
            return Transpiler().transpile(program)
        if target == "assembly":
            return AssemblyEmitter().emit(program)
        if target == "c":
            return CLanguageEmitter().emit(program)
        if target == "cpp":
            return CppEmitter().emit(program)
        if target == "csharp":
            return CSharpEmitter().emit(program)
        if target == "php":
            return PhpEmitter().emit(program)
        if target == "sql":
            return SqlEmitter().emit(program)
        if target == "go":
            return GoEmitter().emit(program)
        if target == "java":
            return JavaEmitter().emit(program)
        if target == "javascript":
            return JavaScriptEmitter().emit(program)
        if target == "perl":
            return PerlEmitter().emit(program)
        if target == "rust":
            return RustEmitter().emit(program)
        if target == "ruby":
            return RubyEmitter().emit(program)
        if target == "r":
            return REmitter().emit(program)
        raise ValueError(f"Unsupported advanced compile target: {target}")

    def _introspect(self, program: nodes.Program, *, module_name: str) -> Dict[str, Any]:
        functions: List[Dict[str, Any]] = []
        classes: List[Dict[str, Any]] = []
        imports: List[str] = []
        payloads: List[str] = []
        embedded_assets: List[Dict[str, Any]] = []
        tasks: List[str] = []

        for statement in program.statements:
            if isinstance(statement, nodes.FunctionDefinition):
                functions.append(self._describe_function(statement))
            elif isinstance(statement, nodes.ClassDefinition):
                classes.append(self._describe_class(statement))
            elif isinstance(statement, nodes.ImportStatement):
                for item in statement.items:
                    imports.append(".".join(item.module))
            elif isinstance(statement, nodes.FromImportStatement):
                module = ".".join(statement.module)
                for item in statement.items:
                    alias = item.alias or item.name
                    imports.append(f"from {module} import {alias}")
            elif isinstance(statement, nodes.PayloadStatement):
                payloads.append(statement.name)
            elif isinstance(statement, nodes.EmbedStatement):
                embedded_assets.append(
                    {
                        "name": statement.name,
                        "language": str(statement.language),
                        "content": self._render_expression(statement.content),
                        "metadata": self._render_expression(statement.metadata)
                        if statement.metadata is not None
                        else None,
                        "line": statement.line,
                    }
                )
            elif isinstance(statement, nodes.TaskStatement):
                tasks.append(statement.name)

        return {
            "module": module_name,
            "imports": sorted(set(imports)),
            "functions": functions,
            "classes": classes,
            "payloads": payloads,
            "embedded_assets": embedded_assets,
            "tasks": tasks,
        }

    def _describe_function(self, statement: nodes.FunctionDefinition) -> Dict[str, Any]:
        parameters = [self._describe_parameter(param) for param in statement.parameters]
        return {
            "name": statement.name,
            "parameters": [param.__dict__ for param in parameters],
            "is_async": statement.is_async,
            "line": statement.line,
            "docstring": statement.docstring,
        }

    def _describe_parameter(self, parameter: nodes.Parameter) -> IntrospectedParameter:
        default_repr = None
        if parameter.default is not None:
            default_repr = self._render_expression(parameter.default)
        return IntrospectedParameter(parameter.name, default_repr, parameter.kind)

    def _describe_class(self, statement: nodes.ClassDefinition) -> Dict[str, Any]:
        bases = [self._render_expression(expr) for expr in statement.bases] or ["object"]
        methods: List[Dict[str, Any]] = []
        for item in statement.body:
            if isinstance(item, nodes.FunctionDefinition):
                methods.append(self._describe_function(item))
        return {
            "name": statement.name,
            "bases": bases,
            "methods": methods,
            "line": statement.line,
            "docstring": statement.docstring,
        }

    def _render_expression(self, expression: Any) -> str:
        if isinstance(expression, nodes.Identifier):
            return expression.name
        if isinstance(expression, nodes.AttributeReference):
            return f"{self._render_expression(expression.value)}.{expression.attribute}"
        if isinstance(expression, nodes.CallExpression):
            args = ", ".join(self._render_expression(arg) for arg in expression.args)
            kwargs = ", ".join(
                f"{key}={self._render_expression(value)}" for key, value in expression.kwargs.items()
            )
            if kwargs:
                args = ", ".join(filter(None, [args, kwargs]))
            return f"{self._render_expression(expression.function)}({args})"
        if isinstance(expression, nodes.UnaryExpression):
            return f"{expression.operator.lower()} {self._render_expression(expression.operand)}"
        if isinstance(expression, nodes.BinaryExpression):
            left = self._render_expression(expression.left)
            right = self._render_expression(expression.right)
            return f"{left} {expression.operator.lower()} {right}"
        if isinstance(expression, nodes.ListExpression):
            items = ", ".join(self._render_expression(item) for item in expression.elements)
            return f"[{items}]"
        if isinstance(expression, nodes.TupleExpression):
            items = ", ".join(self._render_expression(item) for item in expression.elements)
            return f"({items})"
        if isinstance(expression, nodes.DictExpression):
            items = ", ".join(
                f"{self._render_expression(key)}: {self._render_expression(value)}"
                for key, value in expression.entries
            )
            return f"{{{items}}}"
        if isinstance(expression, nodes.SetExpression):
            items = ", ".join(self._render_expression(item) for item in expression.elements)
            return f"{{{items}}}"
        if isinstance(expression, nodes.ListComprehension):
            base = self._render_expression(expression.expression)
            iterable = self._render_expression(expression.iterable)
            clause = f"{base} FOR {expression.iterator} IN {iterable}"
            if expression.condition is not None:
                clause += f" IF {self._render_expression(expression.condition)}"
            return f"[{clause}]"
        if isinstance(expression, nodes.ConditionalExpression):
            true_expr = self._render_expression(expression.if_true)
            cond_expr = self._render_expression(expression.condition)
            false_expr = self._render_expression(expression.if_false)
            return f"{true_expr} IF {cond_expr} ELSE {false_expr}"
        if isinstance(expression, nodes.LambdaExpression):
            params = ", ".join(param.name for param in expression.parameters)
            return f"lambda {params}: {self._render_expression(expression.body)}"
        if isinstance(expression, nodes.AwaitExpression):
            return f"await {self._render_expression(expression.expression)}"
        if isinstance(expression, nodes.IndexReference):
            return f"{self._render_expression(expression.value)}[{self._render_expression(expression.index)}]"
        if isinstance(expression, (str, int, float, bool)):
            return repr(expression)
        if expression is None:
            return "None"
        return repr(expression)


__all__ = [
    "AdvancedCompiler",
    "AdvancedCompileArtifact",
    "IntrospectedClass",
    "IntrospectedFunction",
    "IntrospectedParameter",
]
