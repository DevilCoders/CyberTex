"""Extended helper functions exposed to SAPL programs."""

from __future__ import annotations

import inspect
import io
import re
from functools import partial as _partial, reduce as _reduce
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence


# ---------------------------------------------------------------------------
# Type conversion helpers
# ---------------------------------------------------------------------------


def to_int(value: Any, base: int = 10) -> int:
    """Convert *value* to an ``int`` using an optional base for strings."""

    if isinstance(value, str):
        return int(value, base)
    return int(value)


def to_float(value: Any) -> float:
    """Convert *value* to ``float``."""

    return float(value)


def to_str(value: Any) -> str:
    """Convert *value* to ``str``."""

    return str(value)


def to_bool(value: Any) -> bool:
    """Convert *value* to ``bool`` following Python truthiness rules."""

    return bool(value)


def to_list(value: Iterable[Any]) -> list[Any]:
    """Convert *value* to a list."""

    return list(value)


def to_tuple(value: Iterable[Any]) -> tuple[Any, ...]:
    """Convert *value* to a tuple."""

    return tuple(value)


def to_set(value: Iterable[Any]) -> set[Any]:
    """Convert *value* to a set."""

    return set(value)


def to_bytes(value: Any, encoding: str = "utf-8", errors: str = "strict") -> bytes:
    """Convert *value* to ``bytes``.

    Strings honour the provided *encoding*, other values must already implement
    the buffer protocol.
    """

    if isinstance(value, str):
        return value.encode(encoding, errors)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value)
    raise TypeError(f"Cannot convert {type(value).__name__} to bytes")


# ---------------------------------------------------------------------------
# Object inspection helpers
# ---------------------------------------------------------------------------


def object_describe(obj: Any) -> dict[str, Any]:
    """Return a descriptive dictionary about *obj*."""

    typ = type(obj)
    return {
        "type": typ.__name__,
        "module": typ.__module__,
        "callable": callable(obj),
        "doc": inspect.getdoc(obj) or "",
        "attributes": sorted(
            attr for attr in dir(obj) if not attr.startswith("__")
        ),
    }


def object_members(obj: Any) -> list[str]:
    """Return all attribute names available on *obj*."""

    return sorted(dir(obj))


def object_public_attrs(obj: Any) -> list[str]:
    """Return public, non-callable attributes for *obj*."""

    result: list[str] = []
    for name in dir(obj):
        if name.startswith("__"):
            continue
        value = getattr(obj, name)
        if callable(value):
            continue
        result.append(name)
    return sorted(result)


def object_methods(obj: Any) -> list[str]:
    """Return public method names for *obj*."""

    result: list[str] = []
    for name in dir(obj):
        if name.startswith("__"):
            continue
        if callable(getattr(obj, name)):
            result.append(name)
    return sorted(result)


# ---------------------------------------------------------------------------
# Common functional helpers
# ---------------------------------------------------------------------------


def identity(value: Any) -> Any:
    """Return *value* unchanged."""

    return value


def apply(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Invoke *func* with the provided arguments."""

    return func(*args, **kwargs)


def partial(func: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Callable[..., Any]:
    """Return a callable with pre-bound arguments, mirroring ``functools.partial``."""

    return _partial(func, *args, **kwargs)


def compose(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Compose multiple single-argument callables into one callable."""

    if not functions:
        raise ValueError("compose requires at least one function")

    def composed(value: Any) -> Any:
        result = value
        for func in reversed(functions):
            result = func(result)
        return result

    return composed


def pipe(value: Any, *functions: Callable[[Any], Any]) -> Any:
    """Pipe *value* through a sequence of callables."""

    result = value
    for func in functions:
        result = func(result)
    return result


def filter_list(func: Callable[[Any], bool], iterable: Iterable[Any]) -> list[Any]:
    """Return a concrete list of items matching ``func``."""

    return [item for item in iterable if func(item)]


def map_list(func: Callable[[Any], Any], iterable: Iterable[Any]) -> list[Any]:
    """Return a concrete list after mapping ``func`` across ``iterable``."""

    return [func(item) for item in iterable]


def reduce(func: Callable[[Any, Any], Any], iterable: Iterable[Any], initializer: Any | None = None) -> Any:
    """Fold ``iterable`` using ``func`` similar to :func:`functools.reduce`."""

    if initializer is not None:
        return _reduce(func, iterable, initializer)
    return _reduce(func, iterable)


def flatten(nested: Iterable[Iterable[Any]]) -> list[Any]:
    """Flatten one level of nesting into a list."""

    result: list[Any] = []
    for group in nested:
        result.extend(group)
    return result


# ---------------------------------------------------------------------------
# Blue team helpers
# ---------------------------------------------------------------------------


def blueteam_log_event(
    description: str,
    *,
    severity: str = "info",
    source: str | None = None,
    tags: Sequence[str] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a structured blue-team event record."""

    return {
        "type": "blueteam_event",
        "description": description,
        "severity": severity,
        "source": source or "runtime",
        "tags": list(tags or ()),
        "context": dict(context or {}),
    }


def blueteam_playbook(
    name: str,
    steps: Sequence[str],
    owner: str = "SOC",
    objectives: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Return a SOC playbook definition suitable for reporting."""

    return {
        "type": "blueteam_playbook",
        "name": name,
        "owner": owner,
        "steps": list(steps),
        "objectives": list(objectives or ()),
    }


def blueteam_readiness(score: float, indicators: Sequence[str] | None = None) -> dict[str, Any]:
    """Generate a readiness snapshot, constraining *score* to the 0-1 range."""

    bounded_score = max(0.0, min(score, 1.0))
    return {
        "type": "blueteam_readiness",
        "score": bounded_score,
        "indicators": list(indicators or ()),
    }


# ---------------------------------------------------------------------------
# Red team helpers
# ---------------------------------------------------------------------------


def redteam_objective(
    name: str,
    *,
    tactics: Sequence[str],
    detections: Sequence[str] | None = None,
    impact: str | None = None,
) -> dict[str, Any]:
    """Describe a red-team objective mapped to tactics and detections."""

    return {
        "type": "redteam_objective",
        "name": name,
        "tactics": list(tactics),
        "detections": list(detections or ()),
        "impact": impact or "assessment",
    }


def redteam_campaign(
    title: str,
    objectives: Sequence[dict[str, Any]],
    *,
    operators: Sequence[str] | None = None,
    notes: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Bundle objectives together for a reusable red-team campaign plan."""

    return {
        "type": "redteam_campaign",
        "title": title,
        "objectives": list(objectives),
        "operators": list(operators or ()),
        "notes": list(notes or ()),
    }


def redteam_emulation_matrix(
    mapping: dict[str, Sequence[str]],
    *,
    framework: str = "ATT&CK",
) -> dict[str, Any]:
    """Normalise a tactic-to-technique mapping for reporting pipelines."""

    return {
        "type": "redteam_emulation_matrix",
        "framework": framework,
        "mapping": {tactic: list(techniques) for tactic, techniques in mapping.items()},
    }


# ---------------------------------------------------------------------------
# Purple team helpers
# ---------------------------------------------------------------------------


def purpleteam_alignment(
    *,
    campaign: dict[str, Any],
    readiness: dict[str, Any],
    shared_metrics: Sequence[str] | None = None,
    cadence: str = "monthly",
) -> dict[str, Any]:
    """Fuse red and blue artefacts into an actionable alignment snapshot."""

    return {
        "type": "purpleteam_alignment",
        "campaign": dict(campaign),
        "readiness": dict(readiness),
        "metrics": list(shared_metrics or ()),
        "cadence": cadence,
    }


def purpleteam_exercise_plan(
    name: str,
    *,
    objectives: Sequence[dict[str, Any]],
    detections: Sequence[dict[str, Any]],
    facilitation: Sequence[str] | None = None,
    outcomes: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Describe a purple-team exercise linking detection gaps with objectives."""

    return {
        "type": "purpleteam_exercise",
        "name": name,
        "objectives": list(objectives),
        "detections": list(detections),
        "facilitation": list(facilitation or ()),
        "expected_outcomes": list(outcomes or ()),
    }


def purpleteam_scorecard(
    *,
    alignment: dict[str, Any],
    exercise: dict[str, Any],
    maturity: float,
    notes: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Summarise exercise impact and alignment maturity for reporting."""

    bounded_maturity = max(0.0, min(maturity, 1.0))
    return {
        "type": "purpleteam_scorecard",
        "alignment": dict(alignment),
        "exercise": dict(exercise),
        "maturity": bounded_maturity,
        "notes": list(notes or ()),
    }


# ---------------------------------------------------------------------------
# Regular expression helpers
# ---------------------------------------------------------------------------


_FLAG_ALIASES = {
    "A": re.ASCII,
    "ASCII": re.ASCII,
    "IGNORECASE": re.IGNORECASE,
    "I": re.IGNORECASE,
    "MULTILINE": re.MULTILINE,
    "M": re.MULTILINE,
    "DOTALL": re.DOTALL,
    "S": re.DOTALL,
    "VERBOSE": re.VERBOSE,
    "X": re.VERBOSE,
    "LOCALE": re.LOCALE,
    "L": re.LOCALE,
    "UNICODE": re.UNICODE,
    "U": re.UNICODE,
}


def _resolve_regex_flags(flags: Any) -> int:
    """Normalise *flags* into a value understood by :mod:`re`."""

    if flags in (None, 0):
        return 0
    if isinstance(flags, int):
        return flags
    if isinstance(flags, str):
        flag_value = 0
        for token in flags.replace("|", " ").split():
            key = token.upper()
            if key not in _FLAG_ALIASES:
                raise ValueError(f"Unknown regex flag '{token}'")
            flag_value |= _FLAG_ALIASES[key]
        return flag_value
    if isinstance(flags, Sequence):
        flag_value = 0
        for token in flags:
            flag_value |= _resolve_regex_flags(token)
        return flag_value
    raise TypeError(f"Unsupported flag specification of type {type(flags).__name__}")


def _describe_match(match: re.Match[str] | None) -> dict[str, Any] | None:
    if match is None:
        return None
    return {
        "match": match.group(0),
        "groups": list(match.groups()),
        "groupdict": dict(match.groupdict()),
        "span": list(match.span()),
    }


def regex_compile(pattern: str, flags: Any | None = None) -> re.Pattern[str]:
    """Compile *pattern* using optional *flags* and return a regex object."""

    return re.compile(pattern, _resolve_regex_flags(flags))


def regex_match(pattern: str, text: str, flags: Any | None = None) -> dict[str, Any] | None:
    """Perform ``re.match`` returning a descriptive mapping."""

    compiled = regex_compile(pattern, flags)
    return _describe_match(compiled.match(text))


def regex_search(pattern: str, text: str, flags: Any | None = None) -> dict[str, Any] | None:
    """Perform ``re.search`` returning a descriptive mapping."""

    compiled = regex_compile(pattern, flags)
    return _describe_match(compiled.search(text))


def regex_findall(pattern: str, text: str, flags: Any | None = None) -> list[Any]:
    """Return all non-overlapping matches similar to :func:`re.findall`."""

    compiled = regex_compile(pattern, flags)
    return compiled.findall(text)


def regex_split(
    pattern: str,
    text: str,
    maxsplit: int = 0,
    flags: Any | None = None,
) -> list[str]:
    """Split *text* using a regex pattern."""

    compiled = regex_compile(pattern, flags)
    return compiled.split(text, maxsplit)


def regex_replace(
    pattern: str,
    repl: str,
    text: str,
    count: int = 0,
    flags: Any | None = None,
) -> str:
    """Replace occurrences of *pattern* in *text* with *repl*."""

    compiled = regex_compile(pattern, flags)
    return compiled.sub(repl, text, count=count)


# ---------------------------------------------------------------------------
# String helpers
# ---------------------------------------------------------------------------


def string_upper(value: Any) -> str:
    return str(value).upper()


def string_lower(value: Any) -> str:
    return str(value).lower()


def string_title(value: Any) -> str:
    return str(value).title()


def string_capitalize(value: Any) -> str:
    return str(value).capitalize()


def string_strip(value: Any) -> str:
    return str(value).strip()


def string_lstrip(value: Any) -> str:
    return str(value).lstrip()


def string_rstrip(value: Any) -> str:
    return str(value).rstrip()


def string_replace(value: Any, old: str, new: str, count: int | None = None) -> str:
    text = str(value)
    if count is None:
        return text.replace(old, new)
    return text.replace(old, new, count)


def string_split(value: Any, sep: str | None = None, maxsplit: int = -1) -> list[str]:
    return str(value).split(sep, maxsplit)


def string_join(separator: str, values: Iterable[Any]) -> str:
    return separator.join(map(str, values))


def string_center(value: Any, width: int, fillchar: str = " ") -> str:
    return str(value).center(width, fillchar)


def string_pad_left(value: Any, width: int, fillchar: str = " ") -> str:
    return str(value).rjust(width, fillchar)


def string_pad_right(value: Any, width: int, fillchar: str = " ") -> str:
    return str(value).ljust(width, fillchar)


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------


def file_read_text(path: str, encoding: str = "utf-8") -> str:
    return Path(path).read_text(encoding=encoding)


def file_write_text(path: str, content: str, encoding: str = "utf-8") -> str:
    Path(path).write_text(content, encoding=encoding)
    return path


def file_append_text(path: str, content: str, encoding: str = "utf-8") -> str:
    with Path(path).open("a", encoding=encoding) as handle:
        handle.write(content)
    return path


def file_read_bytes(path: str) -> bytes:
    return Path(path).read_bytes()


def file_write_bytes(path: str, content: bytes) -> str:
    Path(path).write_bytes(content)
    return path


def file_stream(path: str, mode: str = "r", encoding: str | None = "utf-8") -> io.TextIOBase | io.BufferedIOBase:
    return Path(path).open(mode, encoding=encoding if "b" not in mode else None)


# ---------------------------------------------------------------------------
# Exception helpers
# ---------------------------------------------------------------------------


def define_exception(name: str, base: type[BaseException] | None = None) -> type[BaseException]:
    """Create a new exception type with the given *name*."""

    if base is None:
        base = Exception
    if not issubclass(base, BaseException):
        raise TypeError("base must be an exception type")
    return type(name, (base,), {})


def ensure_exception(exc: BaseException | str) -> BaseException:
    """Return an exception instance, instantiating strings along the way."""

    if isinstance(exc, BaseException):
        return exc
    return Exception(str(exc))


def raise_message(exception_type: type[BaseException], message: str) -> None:
    """Raise *exception_type* with *message* immediately."""

    raise exception_type(message)


def rethrow(exception: BaseException) -> None:
    """Re-raise *exception* preserving the existing traceback."""

    raise exception


EXTRA_FUNCTIONS = {
    # Conversion
    "to_int": to_int,
    "to_float": to_float,
    "to_str": to_str,
    "to_bool": to_bool,
    "to_list": to_list,
    "to_tuple": to_tuple,
    "to_set": to_set,
    "to_bytes": to_bytes,
    # Inspection
    "object_describe": object_describe,
    "object_members": object_members,
    "object_public_attrs": object_public_attrs,
    "object_methods": object_methods,
    # Functional helpers
    "identity": identity,
    "apply": apply,
    "partial": partial,
    "compose": compose,
    "pipe": pipe,
    "filter_list": filter_list,
    "map_list": map_list,
    "reduce": reduce,
    "flatten": flatten,
    # Blue team helpers
    "blueteam_log_event": blueteam_log_event,
    "blueteam_playbook": blueteam_playbook,
    "blueteam_readiness": blueteam_readiness,
    # Red team helpers
    "redteam_objective": redteam_objective,
    "redteam_campaign": redteam_campaign,
    "redteam_emulation_matrix": redteam_emulation_matrix,
    # Purple team helpers
    "purpleteam_alignment": purpleteam_alignment,
    "purpleteam_exercise_plan": purpleteam_exercise_plan,
    "purpleteam_scorecard": purpleteam_scorecard,
    # Regular expressions
    "regex_compile": regex_compile,
    "regex_match": regex_match,
    "regex_search": regex_search,
    "regex_findall": regex_findall,
    "regex_split": regex_split,
    "regex_replace": regex_replace,
    # Strings
    "string_upper": string_upper,
    "string_lower": string_lower,
    "string_title": string_title,
    "string_capitalize": string_capitalize,
    "string_strip": string_strip,
    "string_lstrip": string_lstrip,
    "string_rstrip": string_rstrip,
    "string_replace": string_replace,
    "string_split": string_split,
    "string_join": string_join,
    "string_center": string_center,
    "string_pad_left": string_pad_left,
    "string_pad_right": string_pad_right,
    # Files
    "file_read_text": file_read_text,
    "file_write_text": file_write_text,
    "file_append_text": file_append_text,
    "file_read_bytes": file_read_bytes,
    "file_write_bytes": file_write_bytes,
    "file_stream": file_stream,
    # Exceptions
    "define_exception": define_exception,
    "ensure_exception": ensure_exception,
    "raise_message": raise_message,
    "rethrow": rethrow,
}

__all__ = ["EXTRA_FUNCTIONS"]
