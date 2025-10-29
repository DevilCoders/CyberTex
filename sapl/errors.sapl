"""Custom exception hierarchy for SAPL."""

from dataclasses import dataclass


class SAPLError(Exception):
    """Base class for SAPL-related errors."""


@dataclass
class LexError(SAPLError):
    line: int
    column: int
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Lexing error at line {self.line}, column {self.column}: {self.message}"


@dataclass
class ParseError(SAPLError):
    line: int
    column: int
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Parse error at line {self.line}, column {self.column}: {self.message}"


@dataclass
class RuntimeError(SAPLError):
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message
