"""Abstract syntax tree node definitions for SAPL."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence


# ---------------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------------


@dataclass
class Identifier:
    """Represents an identifier that should be resolved at runtime."""

    name: str


@dataclass
class AttributeReference:
    """Access an attribute on an expression."""

    value: Any
    attribute: str


@dataclass
class IndexReference:
    """Access an indexed element within a collection."""

    value: Any
    index: Any


@dataclass
class CallExpression:
    """Represents a call expression."""

    function: Any
    args: List[Any]
    kwargs: Dict[str, Any]


@dataclass
class UnaryExpression:
    """Unary expression such as NOT expr or -expr."""

    operator: str
    operand: Any


@dataclass
class BinaryExpression:
    """Binary expression with an operator and two operands."""

    operator: str
    left: Any
    right: Any


@dataclass
class ListExpression:
    """Literal list."""

    elements: List[Any]


@dataclass
class TupleExpression:
    """Literal tuple."""

    elements: List[Any]


@dataclass
class DictExpression:
    """Literal dictionary expression."""

    entries: List[tuple[Any, Any]]


@dataclass
class SetExpression:
    """Literal set expression."""

    elements: List[Any]


@dataclass
class ListComprehension:
    """List comprehension expression."""

    expression: Any
    iterator: str
    iterable: Any
    condition: Any | None = None


@dataclass
class ConditionalExpression:
    """Conditional expression of the form <true> IF <cond> ELSE <false>."""

    condition: Any
    if_true: Any
    if_false: Any


@dataclass
class LambdaExpression:
    """Lambda expression producing an inline callable."""

    parameters: List["Parameter"]
    body: Any


@dataclass
class AwaitExpression:
    """Await expression used to synchronise asynchronous results."""

    expression: Any


Expression = Any


# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------


@dataclass
class Program:
    statements: List[Any]


@dataclass
class SetStatement:
    name: str
    value: Expression
    line: int


@dataclass
class TargetStatement:
    value: Expression
    line: int


@dataclass
class ScopeStatement:
    value: Expression
    line: int


@dataclass
class PayloadStatement:
    name: str
    value: Expression
    line: int


@dataclass
class EmbedStatement:
    language: str
    name: str
    content: Expression
    line: int
    metadata: Expression | None = None


@dataclass
class TaskStatement:
    name: str
    body: Sequence[Any]
    line: int
    docstring: Optional[str] = None


@dataclass
class ForStatement:
    iterator: str
    iterable: Expression
    body: Sequence[Any]
    line: int


@dataclass
class PortScanStatement:
    ports: Expression
    tool: Expression | None
    line: int


@dataclass
class HttpRequestStatement:
    method: str
    target: Expression
    expect_status: int | None
    contains: Expression | None
    line: int


@dataclass
class FuzzStatement:
    resource: Expression
    method: str | None
    payload: str | None
    payloads_expr: Expression | None
    line: int


@dataclass
class NoteStatement:
    message: Expression
    line: int


@dataclass
class FindingStatement:
    severity: str
    message: Expression
    line: int


@dataclass
class RunStatement:
    command: Expression
    save_as: str | None
    line: int


@dataclass
class ReportStatement:
    destination: Expression
    line: int


@dataclass
class AssignmentStatement:
    """General purpose variable assignment."""

    targets: List[Identifier | AttributeReference | IndexReference]
    value: Expression
    line: int


@dataclass
class AugmentedAssignmentStatement:
    """Augmented assignment (e.g. +=)."""

    target: Identifier | AttributeReference | IndexReference
    operator: str
    value: Expression
    line: int


@dataclass
class ExpressionStatement:
    expression: Expression
    line: int


@dataclass
class IfStatement:
    condition: Expression
    body: Sequence[Any]
    elif_blocks: List[tuple[Expression, Sequence[Any]]]
    else_body: Sequence[Any]
    line: int


@dataclass
class WhileStatement:
    condition: Expression
    body: Sequence[Any]
    else_body: Sequence[Any]
    line: int


@dataclass
class BreakStatement:
    line: int


@dataclass
class ContinueStatement:
    line: int


@dataclass
class PassStatement:
    line: int


@dataclass
class ReturnStatement:
    value: Optional[Expression]
    line: int


@dataclass
class Parameter:
    name: str
    default: Optional[Expression] = None
    kind: str = "positional"


@dataclass
class FunctionDefinition:
    name: str
    parameters: List[Parameter]
    body: Sequence[Any]
    line: int
    docstring: Optional[str] = None
    is_async: bool = False


@dataclass
class WithItem:
    context: Expression
    alias: Optional[str]


@dataclass
class WithStatement:
    items: List[WithItem]
    body: Sequence[Any]
    line: int


@dataclass
class ExceptHandler:
    exception_type: Optional[Expression]
    alias: Optional[str]
    body: Sequence[Any]


@dataclass
class TryStatement:
    body: Sequence[Any]
    handlers: List[ExceptHandler]
    else_body: Sequence[Any]
    finally_body: Sequence[Any]
    line: int


@dataclass
class RaiseStatement:
    value: Optional[Expression]
    line: int


@dataclass
class ImportItem:
    module: List[str]
    alias: Optional[str]


@dataclass
class ImportStatement:
    items: List[ImportItem]
    line: int


@dataclass
class FromImportItem:
    name: str
    alias: Optional[str]


@dataclass
class FromImportStatement:
    module: List[str]
    items: List[FromImportItem]
    line: int


@dataclass
class ClassDefinition:
    name: str
    bases: List[Expression]
    body: Sequence[Any]
    line: int
    docstring: Optional[str] = None


@dataclass
class InputStatement:
    prompt: Optional[Expression]
    target: Optional[str]
    line: int


@dataclass
class OutputStatement:
    value: Expression
    line: int


Statement = Any
