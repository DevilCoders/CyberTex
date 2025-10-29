# Input, Output, and File Handling

SAPL scripts can interactively prompt operators, emit rich output, and manage
filesystem assets required for assessments.

## Interactive Input and Output

* `INPUT "Prompt" AS variable` collects user input. Optional formatters and
  validators can be attached via plugins.
* `OUTPUT` sends formatted strings to the runtime console. Use Python-style
  braces for interpolation and `NOTE` to record findings inside reports.
* `PROMPT` integrates with the website UI to capture structured feedback from
  remote operators, with automatic validation hooks.
* `LOG.debug/info/warn/error` writes to structured logs consumed by the SAPL
  server and website dashboards.

## Structured Reporting

* `REPORT` statements persist findings to Markdown, JSON, or custom formats
  depending on selected backend emitters.
* Combine with the advanced compiler to export documentation, machine code, or
  polyglot payloads while keeping a single source of truth.

## File Access Helpers

* Built-in wrappers around `pathlib.Path` allow reading and writing text files
  with `path_read_text` and `path_write_text`.
* Use `path_glob`, `path_iterdir`, and `path_exists` to enumerate artefacts.
* The extended standard library exposes `open_file`, `read_json`, and
  `write_json` helpers for structured data pipelines.
* Binary workflows rely on `read_bytes`, `write_bytes`, and memory-mapped IO for
  performance-sensitive implants.
* Stream large files with `with open_file(path) AS handle:` blocks to ensure
  handles close correctly even if exceptions occur.

## Remote Resources

* `HTTP.GET`, `HTTP.POST`, and `SFTP` helpers offer cross-platform network
  interactions that respect proxy settings declared in `required.yaml`.
* Use `sapl.io.TempDir()` to stage artefacts during compilation or testing while
  keeping the filesystem tidy.

## Comments for Operators

* Single-line `#` comments annotate tricky IO sections.
* Multi-line `##` blocks can describe the structure of files or credential
  stores that analysts need to touch.
* Docstrings attached to tasks appear in linter and inspector summaries,
  providing a friendly overview inside the CLI.

## Example

Review `examples/io_and_comments.sapl` for a script that guides analysts through
capturing operator input, writing structured findings, and documenting each step
with docstrings and two-line comment blocks.
