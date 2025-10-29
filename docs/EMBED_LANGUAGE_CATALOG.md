# Embedded Language Catalog

The `EMBED` statement now validates the language label against a curated catalog of
polyglot payload types. Using canonical names keeps downstream tooling such as the
advanced compiler, inspector, and website exporter aligned while maintaining
predictable metadata for packaging.

## Supported languages

| Canonical name | Common aliases | Typical usage |
| --- | --- | --- |
| `html` | `htm` | Landing pages, phishing kits, portal overlays |
| `css` | — | Styling for web payloads and dashboards |
| `javascript` | `js` | Client-side automation, telemetry widgets, payload launchers |
| `python` | `py` | Agents, enrichers, API clients, orchestration helpers |
| `php` | — | Web shell fragments and server-side glue |
| `sql` | — | Query packs, detection rules, reporting extracts |
| `go` | `golang` | Portable probes, CLI tooling, server agents |
| `java` | — | JVM-based implants and desktop tooling |
| `perl` | `pl` | Automation scripts, legacy integration points |
| `rust` | — | High-performance agents and cross-platform tooling |
| `ruby` | — | Metasploit-style payload builders and automation |
| `r` | — | Analytics notebooks, reporting summaries |
| `asm` | `assembly`, `nasm`, `masm` | Low-level shellcode and proofs of concept |
| `c` | — | Native utilities and POSIX-compatible implants |
| `c#` | `csharp`, `cs` | Windows automation, CLR implants |
| `c++` | `cpp`, `cxx` | Dropper launchers, cross-platform tooling |

## Validation behaviour

When the interpreter encounters an `EMBED` statement, the supplied language is
normalised and validated. Unknown values raise a runtime error with remediation
instructions. Aliases automatically map to their canonical form, ensuring a
consistent representation across execution results and exported artifacts.

## Extending the catalog

The catalog lives in `sapl/language_registry.sapl`. To add a new language:

1. Append an `EmbeddedLanguage` entry with canonical `name`, optional `aliases`,
   and an optional `description`.
2. Update your documentation to describe the new workflow.
3. Extend tests to cover alias normalisation and runtime validation for the new
   language.

These steps keep the language core, documentation, and validation logic in sync.
