"""Static analysis helpers for describing SAPL scripts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from . import nodes
from .lexer import lex
from .parser import parse


@dataclass
class ParameterSummary:
    name: str
    kind: str
    has_default: bool
    default: Optional[str]


@dataclass
class FunctionSummary:
    name: str
    line: int
    scope: str
    parameters: List[ParameterSummary]
    is_async: bool
    docstring: Optional[str]


@dataclass
class ClassSummary:
    name: str
    line: int
    scope: str
    bases: List[str]
    docstring: Optional[str]


@dataclass
class TaskSummary:
    name: str
    line: int
    scope: str
    docstring: Optional[str]


@dataclass
class ImportSummary:
    module: str
    alias: Optional[str]
    line: int


@dataclass
class PayloadSummary:
    name: str
    expression: str
    line: int


@dataclass
class EmbeddedAssetSummary:
    name: str
    language: str
    scope: str
    content: str
    metadata: Optional[str]
    line: int


@dataclass
class DirectiveSummary:
    kind: str
    expression: str
    line: int


@dataclass
class VariableSummary:
    name: str
    line: int
    scope: str
    kind: str


@dataclass
class ScriptSummary:
    path: Optional[str]
    docstring: Optional[str]
    imports: List[ImportSummary]
    variables: List[VariableSummary]
    payloads: List[PayloadSummary]
    embedded_assets: List[EmbeddedAssetSummary]
    directives: List[DirectiveSummary]
    functions: List[FunctionSummary]
    classes: List[ClassSummary]
    tasks: List[TaskSummary]
    statistics: Dict[str, int]

    def as_dict(self) -> Dict[str, object]:
        return {
            "path": self.path,
            "docstring": self.docstring,
            "imports": [import_summary.__dict__ for import_summary in self.imports],
            "variables": [variable.__dict__ for variable in self.variables],
            "payloads": [payload.__dict__ for payload in self.payloads],
            "embedded_assets": [asset.__dict__ for asset in self.embedded_assets],
            "directives": [directive.__dict__ for directive in self.directives],
            "functions": [
                {
                    "name": function.name,
                    "line": function.line,
                    "scope": function.scope,
                    "docstring": function.docstring,
                    "is_async": function.is_async,
                    "parameters": [parameter.__dict__ for parameter in function.parameters],
                }
                for function in self.functions
            ],
            "classes": [
                {
                    "name": klass.name,
                    "line": klass.line,
                    "scope": klass.scope,
                    "docstring": klass.docstring,
                    "bases": list(klass.bases),
                }
                for klass in self.classes
            ],
            "tasks": [task.__dict__ for task in self.tasks],
            "statistics": dict(self.statistics),
        }


def inspect_path(path: Path) -> ScriptSummary:
    """Inspect a SAPL script from disk."""

    source = path.read_text(encoding="utf-8")
    program = parse(lex(source))
    return _summarise_program(program, path=str(path))


def inspect_source(source: str, *, path: str | None = None) -> ScriptSummary:
    """Inspect SAPL *source* provided as a string."""

    program = parse(lex(source))
    return _summarise_program(program, path=path)


# ---------------------------------------------------------------------------
# Summary helpers
# ---------------------------------------------------------------------------


def _summarise_program(program: nodes.Program, *, path: str | None) -> ScriptSummary:
    imports: List[ImportSummary] = []
    variables: List[VariableSummary] = []
    payloads: List[PayloadSummary] = []
    embedded_assets: List[EmbeddedAssetSummary] = []
    directives: List[DirectiveSummary] = []
    functions: List[FunctionSummary] = []
    classes: List[ClassSummary] = []
    tasks: List[TaskSummary] = []
    module_docstring: Optional[str] = None

    statements = list(program.statements)
    if statements and isinstance(statements[0], nodes.ExpressionStatement) and isinstance(
        statements[0].expression, str
    ):
        module_docstring = statements[0].expression
        statements = statements[1:]

    _walk_statements(
        statements,
        scope=[],
        imports=imports,
        variables=variables,
        payloads=payloads,
        embedded_assets=embedded_assets,
        directives=directives,
        functions=functions,
        classes=classes,
        tasks=tasks,
    )

    statistics = {
        "imports": len(imports),
        "variables": len(variables),
        "payloads": len(payloads),
        "embedded_assets": len(embedded_assets),
        "directives": len(directives),
        "functions": len(functions),
        "classes": len(classes),
        "tasks": len(tasks),
    }

    return ScriptSummary(
        path=path,
        docstring=module_docstring,
        imports=imports,
        variables=variables,
        payloads=payloads,
        embedded_assets=embedded_assets,
        directives=directives,
        functions=functions,
        classes=classes,
        tasks=tasks,
        statistics=statistics,
    )


def _walk_statements(
    statements: Sequence[nodes.Statement],
    *,
    scope: List[str],
    imports: List[ImportSummary],
    variables: List[VariableSummary],
    payloads: List[PayloadSummary],
    embedded_assets: List[EmbeddedAssetSummary],
    directives: List[DirectiveSummary],
    functions: List[FunctionSummary],
    classes: List[ClassSummary],
    tasks: List[TaskSummary],
) -> None:
    scope_name = "::".join(scope) if scope else "<module>"
    for statement in statements:
        if isinstance(statement, nodes.ImportStatement) and not scope:
            for item in statement.items:
                dotted = ".".join(item.module)
                imports.append(ImportSummary(dotted, item.alias, statement.line))
            continue
        if isinstance(statement, nodes.FromImportStatement) and not scope:
            module = ".".join(statement.module)
            for item in statement.items:
                alias = item.alias or item.name
                imports.append(ImportSummary(f"{module}.{item.name}", alias, statement.line))
            continue
        if isinstance(statement, nodes.SetStatement) and not scope:
            variables.append(VariableSummary(statement.name, statement.line, scope_name, "SET"))
            continue
        if isinstance(statement, nodes.AssignmentStatement) and not scope:
            for target in statement.targets:
                if isinstance(target, nodes.Identifier):
                    variables.append(VariableSummary(target.name, statement.line, scope_name, "ASSIGN"))
            continue
        if isinstance(statement, nodes.PayloadStatement) and not scope:
            payloads.append(
                PayloadSummary(statement.name, _describe_expression(statement.value), statement.line)
            )
            continue
        if isinstance(statement, nodes.EmbedStatement):
            content_desc = _describe_expression(statement.content)
            metadata_desc = (
                _describe_expression(statement.metadata)
                if statement.metadata is not None
                else None
            )
            embedded_assets.append(
                EmbeddedAssetSummary(
                    statement.name,
                    str(statement.language),
                    scope_name,
                    content_desc,
                    metadata_desc,
                    statement.line,
                )
            )
            continue
        if isinstance(statement, nodes.TargetStatement) and not scope:
            directives.append(
                DirectiveSummary("TARGET", _describe_expression(statement.value), statement.line)
            )
            continue
        if isinstance(statement, nodes.ScopeStatement) and not scope:
            directives.append(
                DirectiveSummary("SCOPE", _describe_expression(statement.value), statement.line)
            )
            continue
        if isinstance(statement, nodes.ReportStatement) and not scope:
            directives.append(
                DirectiveSummary("REPORT", _describe_expression(statement.destination), statement.line)
            )
            continue
        if isinstance(statement, nodes.TaskStatement):
            task_scope = scope + [statement.name]
            tasks.append(TaskSummary(statement.name, statement.line, scope_name, statement.docstring))
            _walk_statements(
                statement.body,
                scope=task_scope,
                imports=imports,
                variables=variables,
                payloads=payloads,
                embedded_assets=embedded_assets,
                directives=directives,
                functions=functions,
                classes=classes,
                tasks=tasks,
            )
            continue
        if isinstance(statement, nodes.FunctionDefinition):
            parameters = [
                ParameterSummary(
                    parameter.name,
                    parameter.kind,
                    parameter.default is not None,
                    _describe_expression(parameter.default) if parameter.default is not None else None,
                )
                for parameter in statement.parameters
            ]
            function_scope = scope + [statement.name]
            functions.append(
                FunctionSummary(
                    statement.name,
                    statement.line,
                    scope_name,
                    parameters,
                    statement.is_async,
                    statement.docstring,
                )
            )
            _walk_statements(
                statement.body,
                scope=function_scope,
                imports=imports,
                variables=variables,
                payloads=payloads,
                embedded_assets=embedded_assets,
                directives=directives,
                functions=functions,
                classes=classes,
                tasks=tasks,
            )
            continue
        if isinstance(statement, nodes.ClassDefinition):
            bases = [_describe_expression(base) for base in statement.bases]
            class_scope = scope + [statement.name]
            classes.append(
                ClassSummary(statement.name, statement.line, scope_name, bases, statement.docstring)
            )
            _walk_statements(
                statement.body,
                scope=class_scope,
                imports=imports,
                variables=variables,
                payloads=payloads,
                embedded_assets=embedded_assets,
                directives=directives,
                functions=functions,
                classes=classes,
                tasks=tasks,
            )
            continue
        if isinstance(statement, nodes.ExpressionStatement):
            # Ignore stray string literals once docstrings are extracted.
            continue


def _describe_expression(expression: nodes.Expression | object | None) -> str:
    if expression is None:
        return "<none>"
    if isinstance(expression, str):
        return repr(expression)
    if isinstance(expression, (int, float, bool)):
        return repr(expression)
    if isinstance(expression, nodes.Identifier):
        return expression.name
    if isinstance(expression, nodes.AttributeReference):
        return f"{_describe_expression(expression.value)}.{expression.attribute}"
    if isinstance(expression, nodes.IndexReference):
        return f"{_describe_expression(expression.value)}[{_describe_expression(expression.index)}]"
    if isinstance(expression, nodes.CallExpression):
        return f"{_describe_expression(expression.function)}(...)"
    if isinstance(expression, nodes.UnaryExpression):
        return f"{expression.operator}{_describe_expression(expression.operand)}"
    if isinstance(expression, nodes.BinaryExpression):
        left = _describe_expression(expression.left)
        right = _describe_expression(expression.right)
        return f"{left} {expression.operator} {right}"
    if isinstance(expression, nodes.ListExpression):
        return "[" + ", ".join(_describe_expression(item) for item in expression.elements) + "]"
    if isinstance(expression, nodes.TupleExpression):
        return "(" + ", ".join(_describe_expression(item) for item in expression.elements) + ")"
    if isinstance(expression, nodes.SetExpression):
        return "{" + ", ".join(_describe_expression(item) for item in expression.elements) + "}"
    if isinstance(expression, nodes.DictExpression):
        pairs = [
            f"{_describe_expression(key)}: {_describe_expression(value)}" for key, value in expression.entries
        ]
        return "{" + ", ".join(pairs) + "}"
    if isinstance(expression, nodes.ListComprehension):
        rendered = (
            f"[{_describe_expression(expression.expression)} FOR {expression.iterator} IN "
            f"{_describe_expression(expression.iterable)}"
        )
        if expression.condition is not None:
            rendered += f" IF {_describe_expression(expression.condition)}"
        return rendered + "]"
    if isinstance(expression, nodes.ConditionalExpression):
        return (
            f"{_describe_expression(expression.if_true)} IF {_describe_expression(expression.condition)} "
            f"ELSE {_describe_expression(expression.if_false)}"
        )
    if isinstance(expression, nodes.LambdaExpression):
        params = ", ".join(parameter.name for parameter in expression.parameters)
        return f"lambda {params}: ..."
    if isinstance(expression, nodes.AwaitExpression):
        return f"AWAIT {_describe_expression(expression.expression)}"
    return expression.__class__.__name__


__all__ = [
    "ClassSummary",
    "DirectiveSummary",
    "FunctionSummary",
    "ImportSummary",
    "ParameterSummary",
    "PayloadSummary",
    "ScriptSummary",
    "TaskSummary",
    "VariableSummary",
    "inspect_path",
    "inspect_source",
]
