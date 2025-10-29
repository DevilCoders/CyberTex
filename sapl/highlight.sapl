"""Syntax highlighting utilities for SAPL source files."""

from __future__ import annotations

from typing import Dict

from .lexer import KEYWORDS, Token, lex

RESET = "\033[0m"

_THEMES: Dict[str, Dict[str, str]] = {
    "dark": {
        "keyword": "\033[38;5;81m",
        "string": "\033[38;5;114m",
        "number": "\033[38;5;179m",
        "identifier": "\033[38;5;252m",
        "comment": "\033[38;5;240m",
        "punctuation": "\033[38;5;244m",
    },
    "light": {
        "keyword": "\033[38;5;25m",
        "string": "\033[38;5;29m",
        "number": "\033[38;5;130m",
        "identifier": "\033[38;5;237m",
        "comment": "\033[38;5;244m",
        "punctuation": "\033[38;5;102m",
    },
}

_KEYWORD_TYPES = set(KEYWORDS)
_PUNCTUATION_TYPES = {
    "LBRACE",
    "RBRACE",
    "LBRACKET",
    "RBRACKET",
    "LPAREN",
    "RPAREN",
    "COMMA",
    "ASSIGN",
    "COLON",
    "DOT",
}


def available_themes() -> Dict[str, Dict[str, str]]:
    """Return a mapping of theme names to colour definitions."""

    return dict(_THEMES)


def highlight_source(source: str, theme: str = "dark") -> str:
    """Return a colourised version of the given SAPL source."""

    theme_key = theme.lower()
    if theme_key not in _THEMES:
        raise ValueError(f"Unknown theme '{theme}'. Available themes: {', '.join(sorted(_THEMES))}")
    palette = _THEMES[theme_key]
    tokens = lex(source)
    fragments = []
    cursor = 0
    for token in tokens:
        if token.type == "EOF":
            break
        start = token.start if token.start is not None else cursor
        end = token.end if token.end is not None else start
        if start > cursor:
            fragments.append(source[cursor:start])
        fragments.append(_colour_token(token, palette))
        cursor = end
    if cursor < len(source):
        fragments.append(source[cursor:])
    coloured = "".join(fragments)
    if coloured and not coloured.endswith(RESET):
        coloured += RESET
    return coloured


def _colour_token(token: Token, palette: Dict[str, str]) -> str:
    lexeme = token.lexeme or ""
    if not lexeme:
        return lexeme
    if token.type in _KEYWORD_TYPES:
        return f"{palette['keyword']}{lexeme}{RESET}"
    if token.type == "STRING":
        return f"{palette['string']}{lexeme}{RESET}"
    if token.type == "NUMBER":
        return f"{palette['number']}{lexeme}{RESET}"
    if token.type == "COMMENT":
        return f"{palette['comment']}{lexeme}{RESET}"
    if token.type == "IDENT":
        return f"{palette['identifier']}{lexeme}{RESET}"
    if token.type in _PUNCTUATION_TYPES:
        return f"{palette['punctuation']}{lexeme}{RESET}"
    if token.type == "NEWLINE":
        return lexeme
    return lexeme
