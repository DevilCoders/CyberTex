"""Lexical analysis for the extended SAPL language."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Tuple

from .errors import LexError


KEYWORDS = {
    "SET",
    "EMBED",
    "TARGET",
    "SCOPE",
    "PAYLOAD",
    "TASK",
    "PORTSCAN",
    "TOOL",
    "HTTP",
    "EXPECT",
    "CONTAINS",
    "FUZZ",
    "USING",
    "WITH",
    "METHOD",
    "NOTE",
    "FINDING",
    "RUN",
    "SAVE",
    "AS",
    "REPORT",
    "INPUT",
    "OUTPUT",
    "LAMBDA",
    "ASYNC",
    "AWAIT",
    "FOR",
    "IN",
    "IF",
    "ELIF",
    "ELSE",
    "WHILE",
    "BREAK",
    "CONTINUE",
    "PASS",
    "RETURN",
    "DEF",
    "CLASS",
    "TRY",
    "EXCEPT",
    "FINALLY",
    "RAISE",
    "IMPORT",
    "FROM",
    "TRUE",
    "FALSE",
    "NONE",
    "AND",
    "OR",
    "NOT",
}

BOOL_KEYWORDS = {
    "TRUE": True,
    "FALSE": False,
    "NONE": None,
}


OPERATORS: Dict[str, str] = {
    "==": "EQ",
    "!=": "NEQ",
    "<=" : "LTE",
    ">=": "GTE",
    "<": "LT",
    ">": "GT",
    "+=": "PLUSEQ",
    "-=": "MINUSEQ",
    "*=": "STAREQ",
    "/=": "SLASHEQ",
    "//=": "DBLSLASHEQ",
    "%=": "PERCENTEQ",
    "**=": "POWEQ",
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "**": "POWER",
    "/": "SLASH",
    "//": "DBLSLASH",
    "%": "PERCENT",
    "=": "ASSIGN",
    ":": "COLON",
    ".": "DOT",
}


DELIMITERS = {
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
    "{": "LBRACE",
    "}": "RBRACE",
    ",": "COMMA",
}


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int
    lexeme: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None

    def __post_init__(self) -> None:
        if self.lexeme is None:
            self.lexeme = self.value


class Lexer:
    """Converts input text into a stream of tokens."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1
        self._indent_stack: List[int] = [0]
        self._pending: List[Token] = []
        self._at_line_start = True

    # Public API ---------------------------------------------------------

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        for token in self._generate_tokens():
            tokens.append(token)
        # unwind indentation stack at EOF
        while len(self._indent_stack) > 1:
            self._indent_stack.pop()
            tokens.append(self._make_simple_token("DEDENT"))
        tokens.append(Token("EOF", "", self.line, self.column))
        return tokens

    # Internals ---------------------------------------------------------

    def _generate_tokens(self) -> Iterator[Token]:
        while True:
            if self._pending:
                yield self._pending.pop(0)
                continue
            if self._is_at_end:
                break
            if self._at_line_start:
                indent_tokens, has_code = self._handle_indent()
                for token in indent_tokens:
                    yield token
                # if there is no code on the line the indent handler positions
                # us at the newline (or comment) which will be processed below.
                self._at_line_start = False
                if self._is_at_end:
                    break
            char = self._peek()
            if char in " \t\r":
                self._advance()
                continue
            if char == "\n":
                yield self._make_token("NEWLINE", "\n")
                self._advance(new_line=True)
                self._at_line_start = True
                continue
            if char == "#":
                yield self._comment()
                continue
            if char in "\"'":
                yield self._string(char)
                continue
            if char.isdigit():
                yield self._number()
                continue
            if char.isalpha() or char == "_":
                yield self._identifier()
                continue
            if char in DELIMITERS:
                yield self._make_delimiter(char)
                self._advance()
                continue
            op_token = self._operator_token()
            if op_token is not None:
                yield op_token
                continue
            raise LexError(self.line, self.column, f"Unexpected character: {char!r}")

    def _handle_indent(self) -> Tuple[List[Token], bool]:
        # look ahead to compute indentation without consuming comments/newlines
        idx = self.position
        column = self.column
        indent = 0
        text_length = len(self.text)
        while idx < text_length:
            ch = self.text[idx]
            if ch == " ":
                indent += 1
                idx += 1
                column += 1
                continue
            if ch == "\t":
                indent += 4
                idx += 1
                column += 1
                continue
            if ch == "\r":
                idx += 1
                continue
            break
        if idx >= text_length:
            self.position = idx
            self.column = column
            return ([], False)
        next_char = self.text[idx]
        if next_char == "\n":
            # blank line
            self.position = idx
            self.column = column
            return ([], False)
        if next_char == "#":
            # indentation is ignored for pure comment lines
            self.position = idx
            self.column = column
            return ([], False)
        # consume the indentation characters
        self.position = idx
        self.column = column
        current = self._indent_stack[-1]
        if indent == current:
            return ([], True)
        if indent > current:
            self._indent_stack.append(indent)
            return ([self._make_simple_token("INDENT")], True)
        tokens: List[Token] = []
        while indent < self._indent_stack[-1]:
            self._indent_stack.pop()
            tokens.append(self._make_simple_token("DEDENT"))
        if indent != self._indent_stack[-1]:
            raise LexError(self.line, self.column, "Unbalanced indentation")
        return (tokens, True)

    def _make_simple_token(self, token_type: str) -> Token:
        return Token(token_type, "", self.line, self.column, "", self.position, self.position)

    def _make_token(self, token_type: str, value: str) -> Token:
        start_index = self.position
        return Token(token_type, value, self.line, self.column, value, start_index, start_index + len(value))

    def _make_delimiter(self, char: str) -> Token:
        token_type = DELIMITERS[char]
        return Token(token_type, char, self.line, self.column, char, self.position, self.position + 1)

    def _operator_token(self) -> Optional[Token]:
        # match the longest possible operator
        for length in (3, 2, 1):
            candidate = self._peek_many(length)
            if candidate is None:
                continue
            if candidate in OPERATORS:
                token_type = OPERATORS[candidate]
                start_index = self.position
                token = Token(token_type, candidate, self.line, self.column, candidate, start_index, start_index + length)
                self._advance_many(length)
                return token
        return None

    def _comment(self) -> Token:
        start_line, start_column = self.line, self.column
        start_index = self.position
        self._advance()  # consume the leading '#'
        if not self._is_at_end and self._peek() == "#":
            self._advance()  # consume the second '#'
            return self._block_comment(start_line, start_column, start_index)

        lexeme_chars = ["#"]
        chars: List[str] = []
        while not self._is_at_end and self._peek() != "\n":
            ch = self._peek()
            lexeme_chars.append(ch)
            chars.append(ch)
            self._advance()
        lexeme = "".join(lexeme_chars)
        return Token(
            "COMMENT",
            "".join(chars),
            start_line,
            start_column,
            lexeme,
            start_index,
            start_index + len(lexeme),
        )

    def _block_comment(self, start_line: int, start_column: int, start_index: int) -> Token:
        """Parse a ``##`` delimited multi-line comment."""

        lexeme_chars = ["#", "#"]
        chars: List[str] = []
        at_line_start = True

        while not self._is_at_end:
            if self._peek_many(2) == "##" and at_line_start:
                lexeme_chars.extend(["#", "#"])
                self._advance_many(2)
                break

            ch = self._peek()
            lexeme_chars.append(ch)
            chars.append(ch)
            if ch == "\n":
                self._advance(new_line=True)
                at_line_start = True
            else:
                self._advance()
                if ch not in (" ", "\t"):
                    at_line_start = False

        end_index = self.position
        lexeme = "".join(lexeme_chars)
        return Token(
            "COMMENT",
            "".join(chars),
            start_line,
            start_column,
            lexeme,
            start_index,
            end_index,
        )

    def _string(self, delimiter: str) -> Token:
        start_line, start_column = self.line, self.column
        start_index = self.position
        self._advance()  # consume opening quote
        chars: List[str] = []
        lexeme_chars = [delimiter]
        while not self._is_at_end:
            ch = self._peek()
            if ch == delimiter:
                lexeme_chars.append(delimiter)
                self._advance()
                lexeme = "".join(lexeme_chars)
                return Token(
                    "STRING",
                    "".join(chars),
                    start_line,
                    start_column,
                    lexeme,
                    start_index,
                    start_index + len(lexeme),
                )
            if ch == "\\":
                lexeme_chars.append("\\")
                self._advance()
                if self._is_at_end:
                    raise LexError(start_line, start_column, "Unterminated string literal")
                escape_char = self._peek()
                lexeme_chars.append(escape_char)
                escape_map = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    "\\": "\\",
                    "\"": "\"",
                    "'": "'",
                }
                chars.append(escape_map.get(escape_char, escape_char))
                self._advance()
                continue
            chars.append(ch)
            lexeme_chars.append(ch)
            self._advance()
        raise LexError(start_line, start_column, "Unterminated string literal")

    def _number(self) -> Token:
        start_line, start_column = self.line, self.column
        start_index = self.position
        value_chars = [self._peek()]
        self._advance()
        while not self._is_at_end and self._peek().isdigit():
            value_chars.append(self._peek())
            self._advance()
        if not self._is_at_end and self._peek() == ".":
            value_chars.append(".")
            self._advance()
            while not self._is_at_end and self._peek().isdigit():
                value_chars.append(self._peek())
                self._advance()
        lexeme = "".join(value_chars)
        return Token("NUMBER", lexeme, start_line, start_column, lexeme, start_index, start_index + len(lexeme))

    def _identifier(self) -> Token:
        start_line, start_column = self.line, self.column
        start_index = self.position
        value_chars = [self._peek()]
        self._advance()
        while not self._is_at_end and (self._peek().isalnum() or self._peek() == "_"):
            value_chars.append(self._peek())
            self._advance()
        value = "".join(value_chars)
        upper_value = value.upper()
        if upper_value in KEYWORDS:
            return Token(upper_value, upper_value, start_line, start_column, value, start_index, start_index + len(value))
        return Token("IDENT", value, start_line, start_column, value, start_index, start_index + len(value))

    # Helper utilities --------------------------------------------------

    def _advance(self, *, new_line: bool = False) -> None:
        self.position += 1
        if new_line:
            self.line += 1
            self.column = 1
            self._at_line_start = True
        else:
            self.column += 1

    def _advance_many(self, count: int) -> None:
        for _ in range(count):
            if self._is_at_end:
                return
            if self._peek() == "\n":
                self._advance(new_line=True)
            else:
                self._advance()

    def _peek(self) -> str:
        return self.text[self.position]

    def _peek_many(self, count: int) -> Optional[str]:
        end = self.position + count
        if end > len(self.text):
            return None
        return self.text[self.position:end]

    @property
    def _is_at_end(self) -> bool:
        return self.position >= len(self.text)


def lex(text: str) -> List[Token]:
    """Utility function that tokenizes the provided text."""

    return Lexer(text).tokenize()
