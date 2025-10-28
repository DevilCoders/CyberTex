# Working with Data Structures

SAPL embraces Python-inspired collections so security researchers can manipulate
inputs, results, and reports naturally.

## Simple Types

* Integers, floats, booleans, and strings behave as expected. Numbers support
  binary, octal, and hexadecimal literal prefixes.
* Strings honour escape sequences, triple-quoted docstrings, and block comments
  can provide ancillary documentation.

## Lists

* Literal lists use `[value, value]` syntax and support comprehension forms such
  as `[payload FOR payload IN payloads IF payload.enabled]`.
* List methods mirror Python via the standard library helper functions
  `list_append`, `list_extend`, `filter_list`, `map_list`, and `flatten`.

## Tuples

* Tuples use parentheses—`("analyst", "hunter2")`—and are ideal for
  multi-assignment.
* Single-value tuples add a trailing comma. Tuple unpacking supports destructing
  nested collections.

## Dictionaries

* Dictionaries use `{key: value}` and can mix primitive and structured keys.
* The runtime exposes `dict_get`, `dict_items`, and `dict_merge` helpers for
  defensive merging of partial results.

## Sets

* Set literals use `{value, value}` and support operations like union, subset,
  and difference via helper functions `set_union`, `set_difference`, and
  `set_intersection`.
* Comprehensions apply to sets using `{value FOR value IN values}`.

## Advanced Transformations

* Comprehensions work for lists, sets, and dictionaries.
* Generator expressions feed directly into helper utilities such as `any`,
  `all`, or the `pipe` combinator.

## Type Conversion

* The extended standard library provides `to_int`, `to_float`, `to_str`,
  `to_bool`, `to_list`, `to_tuple`, `to_set`, and `to_bytes` for easy coercion.
* `object_describe`, `object_members`, and `object_methods` offer introspection
  for dynamically imported modules or runtime objects.

Explore `examples/data_structures_walkthrough.sapl` for an end-to-end tour that
combines collections, comprehensions, and helper utilities in a reporting
workflow.
