"""Registry describing languages recognised by the ``EMBED`` statement."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping


@dataclass(frozen=True)
class EmbeddedLanguage:
    """Metadata describing an embeddable language."""

    name: str
    aliases: tuple[str, ...] = ()
    description: str | None = None

    def matches(self, value: str) -> bool:
        probe = value.lower()
        return probe == self.name or probe in self.aliases


# Canonical catalogue ordered by how frequently the payloads are expected to
# appear within security automation playbooks.
EMBEDDED_LANGUAGES: tuple[EmbeddedLanguage, ...] = (
    EmbeddedLanguage("html", aliases=("htm",), description="HyperText Markup Language"),
    EmbeddedLanguage("css", description="Cascading Style Sheets"),
    EmbeddedLanguage("javascript", aliases=("js",), description="JavaScript / ECMAScript"),
    EmbeddedLanguage("python", aliases=("py",), description="Python scripts"),
    EmbeddedLanguage("php"),
    EmbeddedLanguage("sql"),
    EmbeddedLanguage("go", aliases=("golang",)),
    EmbeddedLanguage("java"),
    EmbeddedLanguage("perl"),
    EmbeddedLanguage("rust"),
    EmbeddedLanguage("ruby"),
    EmbeddedLanguage("r"),
    EmbeddedLanguage("asm", aliases=("assembly", "nasm", "masm")),
    EmbeddedLanguage("c"),
    EmbeddedLanguage("c#", aliases=("csharp", "cs")),
    EmbeddedLanguage("c++", aliases=("cpp", "cxx")),
)

_LANGUAGE_LOOKUP: Dict[str, EmbeddedLanguage] = {}
for language in EMBEDDED_LANGUAGES:
    _LANGUAGE_LOOKUP[language.name] = language
    for alias in language.aliases:
        _LANGUAGE_LOOKUP[alias] = language


def normalise_embed_language(value: str) -> str:
    """Return a canonical language name recognised by ``EMBED``.

    Raises:
        ValueError: if *value* does not match any registered language.
    """

    probe = value.lower()
    match = _LANGUAGE_LOOKUP.get(probe)
    if match is None:
        raise ValueError(
            "Unsupported embedded language '{}'. Register the language in "
            "sapl.language_registry.EMBEDDED_LANGUAGES or update your playbook "
            "to use a supported alias.".format(value)
        )
    return match.name


def available_embed_languages() -> Mapping[str, EmbeddedLanguage]:
    """Return a mapping of canonical names to language definitions."""

    return {language.name: language for language in EMBEDDED_LANGUAGES}


__all__ = [
    "EMBEDDED_LANGUAGES",
    "EmbeddedLanguage",
    "available_embed_languages",
    "normalise_embed_language",
]
