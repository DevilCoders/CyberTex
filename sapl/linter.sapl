"""Static analysis for SAPL programs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Sequence, Set

from . import nodes
from .lexer import lex
from .parser import parse


@dataclass
class LintMessage:
    """Represents a single linter diagnostic."""

    severity: str
    message: str
    line: int

    def format(self) -> str:
        return f"{self.severity}: line {self.line}: {self.message}"


_PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
_BUILTIN_NAMES = {"target", "targets", "scope"}


class Linter:
    """Analyse an AST and produce lint diagnostics."""

    def __init__(self) -> None:
        self.messages: List[LintMessage] = []
        self.defined_variables: Dict[str, int] = {}
        self.defined_payloads: Dict[str, int] = {}
        self.used_variables: Set[str] = set()
        self.used_payloads: Set[str] = set()
        self.identifier_references: Dict[str, List[int]] = {}
        self.placeholder_references: Dict[str, List[int]] = {}
        self.payload_placeholder_references: Dict[str, List[int]] = {}
        self.payload_identifier_references: Dict[str, List[int]] = {}
    def lint(self, program: nodes.Program) -> List[LintMessage]:
        for statement in program.statements:
            self._visit_statement(statement, ())
        self._finalise()
        return sorted(self.messages, key=lambda msg: (msg.line, msg.severity, msg.message))

    # Visiting -----------------------------------------------------------

    def _visit_statement(self, statement: nodes.Statement, active_loops: Sequence[str]) -> None:
        if isinstance(statement, nodes.SetStatement):
            self.defined_variables.setdefault(statement.name, statement.line)
            self._process_expression(statement.value, statement.line, active_loops)
            return
        if isinstance(statement, nodes.TargetStatement):
            self._process_expression(statement.value, statement.line, active_loops)
            return
        if isinstance(statement, nodes.ScopeStatement):
            self._process_expression(statement.value, statement.line, active_loops)
            return
        if isinstance(statement, nodes.PayloadStatement):
            self.defined_payloads.setdefault(statement.name, statement.line)
            self._process_expression(statement.value, statement.line, active_loops)
            return
        if isinstance(statement, nodes.TaskStatement):
            if not statement.body:
                self._add_warning(statement.line, f"Task '{statement.name}' has no statements")
            if statement.docstring:
                self._process_string(statement.docstring, statement.line, active_loops)
            for inner in statement.body:
                self._visit_statement(inner, active_loops)
            return
        if isinstance(statement, nodes.ForStatement):
            self._process_expression(statement.iterable, statement.line, active_loops)
            next_loops = tuple(active_loops) + (statement.iterator,)
            for inner in statement.body:
                self._visit_statement(inner, next_loops)
            return
        if isinstance(statement, nodes.PortScanStatement):
            self._process_expression(statement.ports, statement.line, active_loops)
            if statement.tool is not None:
                self._process_expression(statement.tool, statement.line, active_loops)
            return
        if isinstance(statement, nodes.HttpRequestStatement):
            self._process_expression(statement.target, statement.line, active_loops)
            if statement.contains is not None:
                self._process_expression(statement.contains, statement.line, active_loops)
            return
        if isinstance(statement, nodes.FuzzStatement):
            self._process_expression(statement.resource, statement.line, active_loops)
            if statement.payload is not None:
                self.used_payloads.add(statement.payload)
                self.payload_identifier_references.setdefault(statement.payload, []).append(statement.line)
            if statement.payloads_expr is not None:
                self._process_expression(statement.payloads_expr, statement.line, active_loops)
            return
        if isinstance(statement, nodes.NoteStatement):
            self._process_expression(statement.message, statement.line, active_loops)
            return
        if isinstance(statement, nodes.FindingStatement):
            self._process_expression(statement.message, statement.line, active_loops)
            return
        if isinstance(statement, nodes.RunStatement):
            self._process_expression(statement.command, statement.line, active_loops)
            return
        if isinstance(statement, nodes.ReportStatement):
            self._process_expression(statement.destination, statement.line, active_loops)
            return
        if isinstance(statement, nodes.InputStatement):
            if statement.prompt is not None:
                self._process_expression(statement.prompt, statement.line, active_loops)
            if statement.target is not None:
                self.defined_variables.setdefault(statement.target, statement.line)
            return
        if isinstance(statement, nodes.OutputStatement):
            self._process_expression(statement.value, statement.line, active_loops)
            return
        if isinstance(statement, nodes.IfStatement):
            self._process_expression(statement.condition, statement.line, active_loops)
            for inner in statement.body:
                self._visit_statement(inner, active_loops)
            for cond, body in statement.elif_blocks:
                self._process_expression(cond, statement.line, active_loops)
                for inner in body:
                    self._visit_statement(inner, active_loops)
            for inner in statement.else_body:
                self._visit_statement(inner, active_loops)
            return
        if isinstance(statement, nodes.WhileStatement):
            self._process_expression(statement.condition, statement.line, active_loops)
            next_loops = tuple(active_loops) + ("<while>",)
            for inner in statement.body:
                self._visit_statement(inner, next_loops)
            for inner in statement.else_body:
                self._visit_statement(inner, active_loops)
            return
        if isinstance(statement, nodes.BreakStatement):
            if not active_loops:
                self._add_error(statement.line, "BREAK used outside of a loop")
            return
        if isinstance(statement, nodes.ContinueStatement):
            if not active_loops:
                self._add_error(statement.line, "CONTINUE used outside of a loop")
            return
        if isinstance(statement, nodes.PassStatement):
            return
        if isinstance(statement, nodes.ReturnStatement):
            if statement.value is not None:
                self._process_expression(statement.value, statement.line, active_loops)
            return
        if isinstance(statement, nodes.FunctionDefinition):
            self.defined_variables.setdefault(statement.name, statement.line)
            for param in statement.parameters:
                if param.default is not None:
                    self._process_expression(param.default, statement.line, active_loops)
            if statement.docstring:
                self._process_string(statement.docstring, statement.line, ())
            parameter_scope = tuple(param.name for param in statement.parameters)
            for inner in statement.body:
                self._visit_statement(inner, parameter_scope)
            return
        if isinstance(statement, nodes.ExpressionStatement):
            self._process_expression(statement.expression, statement.line, active_loops)
            return
        if isinstance(statement, nodes.AssignmentStatement):
            for target in statement.targets:
                self._register_assignment_target(target, statement.line)
            self._process_expression(statement.value, statement.line, active_loops)
            return
        if isinstance(statement, nodes.AugmentedAssignmentStatement):
            self._process_expression(statement.target, statement.line, active_loops)
            self._process_expression(statement.value, statement.line, active_loops)
            return
        if isinstance(statement, nodes.WithStatement):
            for item in statement.items:
                self._process_expression(item.context, statement.line, active_loops)
                if item.alias:
                    self.defined_variables.setdefault(item.alias, statement.line)
            for inner in statement.body:
                self._visit_statement(inner, active_loops)
            return
        if isinstance(statement, nodes.TryStatement):
            for inner in statement.body:
                self._visit_statement(inner, active_loops)
            for handler in statement.handlers:
                if handler.exception_type is not None:
                    self._process_expression(handler.exception_type, statement.line, active_loops)
                if handler.alias:
                    self.defined_variables.setdefault(handler.alias, statement.line)
                for inner in handler.body:
                    self._visit_statement(inner, active_loops)
            for inner in statement.else_body:
                self._visit_statement(inner, active_loops)
            for inner in statement.finally_body:
                self._visit_statement(inner, active_loops)
            return
        if isinstance(statement, nodes.RaiseStatement):
            if statement.value is not None:
                self._process_expression(statement.value, statement.line, active_loops)
            return
        if isinstance(statement, nodes.ImportStatement):
            for item in statement.items:
                alias = item.alias or item.module[-1]
                self.defined_variables.setdefault(alias, statement.line)
            return
        if isinstance(statement, nodes.FromImportStatement):
            for item in statement.items:
                if item.name == "*":
                    continue
                alias = item.alias or item.name
                self.defined_variables.setdefault(alias, statement.line)
            return
        if isinstance(statement, nodes.ClassDefinition):
            self.defined_variables.setdefault(statement.name, statement.line)
            for base in statement.bases:
                self._process_expression(base, statement.line, active_loops)
            if statement.docstring:
                self._process_string(statement.docstring, statement.line, ())
            for inner in statement.body:
                self._visit_statement(inner, ())
            return

    # Expression handling -----------------------------------------------

    def _process_expression(self, expression: nodes.Expression, line: int, active_loops: Sequence[str]) -> None:
        if isinstance(expression, nodes.Identifier):
            self._record_identifier(expression.name, line, active_loops)
            return
        if isinstance(expression, nodes.AttributeReference):
            self._process_expression(expression.value, line, active_loops)
            return
        if isinstance(expression, nodes.IndexReference):
            self._process_expression(expression.value, line, active_loops)
            self._process_expression(expression.index, line, active_loops)
            return
        if isinstance(expression, nodes.CallExpression):
            self._process_expression(expression.function, line, active_loops)
            for arg in expression.args:
                self._process_expression(arg, line, active_loops)
            for value in expression.kwargs.values():
                self._process_expression(value, line, active_loops)
            return
        if isinstance(expression, nodes.UnaryExpression):
            self._process_expression(expression.operand, line, active_loops)
            return
        if isinstance(expression, nodes.BinaryExpression):
            self._process_expression(expression.left, line, active_loops)
            self._process_expression(expression.right, line, active_loops)
            return
        if isinstance(expression, nodes.ListExpression):
            for item in expression.elements:
                self._process_expression(item, line, active_loops)
            return
        if isinstance(expression, nodes.TupleExpression):
            for item in expression.elements:
                self._process_expression(item, line, active_loops)
            return
        if isinstance(expression, nodes.DictExpression):
            for key, value in expression.entries:
                self._process_expression(key, line, active_loops)
                self._process_expression(value, line, active_loops)
            return
        if isinstance(expression, nodes.SetExpression):
            for item in expression.elements:
                self._process_expression(item, line, active_loops)
            return
        if isinstance(expression, nodes.ListComprehension):
            self._process_expression(expression.iterable, line, active_loops)
            loop_scope = tuple(active_loops) + (expression.iterator,)
            if expression.condition is not None:
                self._process_expression(expression.condition, line, loop_scope)
            self._process_expression(expression.expression, line, loop_scope)
            return
        if isinstance(expression, nodes.ConditionalExpression):
            self._process_expression(expression.condition, line, active_loops)
            self._process_expression(expression.if_true, line, active_loops)
            self._process_expression(expression.if_false, line, active_loops)
            return
        if isinstance(expression, nodes.LambdaExpression):
            for param in expression.parameters:
                if param.default is not None:
                    self._process_expression(param.default, line, active_loops)
            lambda_scope = tuple(active_loops) + tuple(param.name for param in expression.parameters)
            self._process_expression(expression.body, line, lambda_scope)
            return
        if isinstance(expression, nodes.AwaitExpression):
            self._process_expression(expression.expression, line, active_loops)
            return
        if isinstance(expression, nodes.AssignmentStatement):  # defensive
            self._visit_statement(expression, active_loops)
            return
        if isinstance(expression, str):
            self._process_string(expression, line, active_loops)
            return
        if isinstance(expression, (list, tuple)):
            for item in expression:
                self._process_expression(item, line, active_loops)
            return

    def _process_string(self, value: str, line: int, active_loops: Sequence[str]) -> None:
        for match in _PLACEHOLDER_RE.finditer(value):
            name = match.group(1)
            if name in _BUILTIN_NAMES:
                continue
            if name in active_loops:
                continue
            if name.startswith("payload_"):
                payload_name = name[len("payload_"):]
                self.used_payloads.add(payload_name)
                self.payload_placeholder_references.setdefault(payload_name, []).append(line)
            else:
                self.used_variables.add(name)
                self.placeholder_references.setdefault(name, []).append(line)

    def _record_identifier(self, name: str, line: int, active_loops: Sequence[str]) -> None:
        if name in _BUILTIN_NAMES:
            return
        if name in active_loops:
            return
        if name in self.defined_payloads:
            self.used_payloads.add(name)
            return
        self.used_variables.add(name)
        self.identifier_references.setdefault(name, []).append(line)

    def _register_assignment_target(self, target: nodes.Identifier | nodes.AttributeReference | nodes.IndexReference, line: int) -> None:
        if isinstance(target, nodes.Identifier):
            self.defined_variables.setdefault(target.name, line)
        elif isinstance(target, (nodes.AttributeReference, nodes.IndexReference)):
            # attribute and index assignments affect existing objects; we still
            # walk their expressions so that identifiers are recorded
            self._process_expression(target, line, ())

    # Finalisation ------------------------------------------------------

    def _finalise(self) -> None:
        for name, line in self.defined_variables.items():
            if name not in self.used_variables:
                self._add_warning(line, f"Variable '{name}' is defined but never used")
        for name, line in self.defined_payloads.items():
            if name not in self.used_payloads:
                self._add_warning(line, f"Payload '{name}' is defined but never used")
        for name, refs in self.identifier_references.items():
            if name not in self.defined_variables:
                self._add_error(min(refs), f"Identifier '{name}' is not defined")
        for name, refs in self.placeholder_references.items():
            if name not in self.defined_variables:
                self._add_warning(min(refs), f"Placeholder '{{{name}}}' may be undefined")
        for name, refs in {**self.payload_placeholder_references, **self.payload_identifier_references}.items():
            if name not in self.defined_payloads:
                self._add_error(min(refs), f"Payload '{name}' is not defined")

    # Utilities ---------------------------------------------------------

    def _add_error(self, line: int, message: str) -> None:
        self.messages.append(LintMessage("ERROR", message, line))

    def _add_warning(self, line: int, message: str) -> None:
        self.messages.append(LintMessage("WARNING", message, line))


def lint_program(program: nodes.Program) -> List[LintMessage]:
    """Run the linter on a parsed SAPL program."""

    return Linter().lint(program)


def lint_source(source: str) -> List[LintMessage]:
    """Parse and lint the provided SAPL source text."""

    tokens = lex(source)
    program = parse(tokens)
    return lint_program(program)
