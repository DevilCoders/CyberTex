# Working With Regular Expressions in SAPL

SAPL exposes first-class regular-expression helpers that build upon Python's `re` module. These helpers simplify common operations and return structured results that are easy to consume inside SAPL scripts.

## Available Helpers

The following built-ins are available once the runtime is initialised:

| Function | Description |
| --- | --- |
| `regex_compile(pattern, flags=None)` | Returns a compiled regex object for repeated use. |
| `regex_match(pattern, text, flags=None)` | Performs an anchored match returning a dictionary with the match, groups, named groups, and span. |
| `regex_search(pattern, text, flags=None)` | Finds the first occurrence within the text. |
| `regex_findall(pattern, text, flags=None)` | Returns a list of all matches. |
| `regex_split(pattern, text, maxsplit=0, flags=None)` | Splits the text using a regex delimiter. |
| `regex_replace(pattern, repl, text, count=0, flags=None)` | Replaces occurrences with the replacement string. |

## Flag Handling

Flags can be passed as integers, strings, or iterables. String values are case-insensitive and support aliases such as `"ignorecase"`, `"i"`, `"multiline"`, and `"m"`. Multiple flags can be supplied using whitespace or `|` separators:

```sapl
SET matches = regex_findall("^host=(?P<name>\\w+)", payload, flags="ignorecase | multiline")
```

## Structured Matches

`regex_match` and `regex_search` return dictionaries with the following keys:

* `match` – the full matched substring.
* `groups` – an ordered list of capture groups.
* `groupdict` – named capture groups as a dictionary.
* `span` – the start and end offsets.

Example:

```sapl
SET result = regex_search("user=(?P<user>\\w+)", "user=analyst id=42")
IF result:
    NOTE "Matched user {result['groupdict']['user']}"
```

## Integration With Tasks

Combine regex helpers with tasks to parse logs or extract indicators:

```sapl
TASK "Parse application logs":
    SET entries = regex_findall("ERROR\\s+(?P<code>\\d+)", log_payload)
    FOR entry IN entries:
        FINDING medium "Observed failure code {entry['code']}"
```

For multi-stage parsing, chain regex calls with list comprehensions:

```sapl
SET indicators = [match['groupdict']
                  FOR match IN regex_findall(pattern, payload)
                  IF match['groupdict']['tld'] IN allowed_tlds]
```

This approach keeps transformations succinct while remaining readable.

## Testing Regex-Based Logic

Leverage `sapl-test` to validate regex-heavy utilities. Place regex helper assertions inside `test_` functions and execute `sapl-test path/to/tests` to ensure patterns behave as expected.

## Performance and Maintainability

* Reuse compiled patterns (`regex_compile`) for tight loops or large datasets.
* Document complex expressions with inline comments and verbose mode (`(?x)`)
  to aid future reviewers.
* The advanced compiler flags catastrophic backtracking during `--analyze`.
  Address warnings by tightening quantifiers or using atomic groups where
  available.
