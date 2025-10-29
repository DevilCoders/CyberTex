# CyberTex SAPL

Special Advanced Programming Language (SAPL) is a research-friendly language for cybersecurity professionals, red teamers, bug bounty hunters, and automation enthusiasts. SAPL merges a concise indentation-based syntax with a battery of offensive-security primitives, a dynamic runtime, and multiple compilation backends so that complex engagements can be modelled, linted, highlighted, executed, or re-targeted with ease.

## Highlights

- **Unified toolchain** – run, lint, highlight, transpile, emit pseudo machine code, or execute bytecode straight from the CLI.
- **Rich language core** – indentation-based blocks, first-class functions, classes, error handling, context managers, comprehensions, and direct access to over 90 curated built-ins.
- **Extended helper suite** – one-call type conversion, object inspection, functional utilities, and file helpers ready for playbook logic or quick prototyping.
- **Interactive ergonomics** – docstrings on tasks, functions, and classes plus dedicated INPUT/OUTPUT statements and literal set support for richer data modelling.
- **Readable syntax upgrades** – double-hash block comments for multi-line annotations and a refreshed style guide aimed at easy onboarding.
- **Asynchronous execution** – declare `ASYNC DEF` routines and `AWAIT` their results to orchestrate non-blocking workflows directly inside playbooks.
- **Domain primitives** – declarative statements for targets, payload management, fuzzing, HTTP checks, recon tasks, reporting, and findings.
- **Standard library gateway** – safe access to major Python standard library modules grouped by operating system services, persistence, networking, concurrency, mathematics, text processing, and security tooling.
- **Extensible backends** – experiment with machine-code inspired instruction streams, a compact bytecode format plus virtual machine, or Python source transpilation for integration with existing tooling.
- **Polyglot emitters** – translate SAPL playbooks into pseudo assembly, C, C++, C#, PHP, SQL, Go, Java, JavaScript, Perl, Rust, Ruby, or R listings for collaborative reviews with systems programmers.
- **Regex and analytics helpers** – dedicated `regex_*` built-ins wrap Python’s `re` module and return structured results for log parsing or payload analysis.
- **Purple-team aware helpers** – structured blue- and red-team primitives model readiness metrics, response playbooks, and offensive campaigns side by side.
- **Plugin ecosystem** – load Python plugins via `--plugin` or `--plugin-dir` to register bespoke built-ins before execution, compilation, or testing.
- **Embedded asset bundling** – register multi-language payloads with `EMBED`, attach metadata, and surface them across the CLI, inspector, and advanced compiler for packaging.
- **Built-in testing harness** – run `python -m sapl test` to execute SAPL-native test suites alongside Python-based unit tests.
- **Interactive CLI upgrades** – launch a stateful shell, inspect scripts without execution, and manage the bundled website straight from the CLI.

## Installation & quick start

```bash
pip install -r requirements.txt  # pytest for development tooling

# Execute a playbook and render a structured engagement plan
python -m sapl run examples/basic.sapl

# Run static analysis
python -m sapl lint examples/basic.sapl

# Syntax highlight directly in the terminal
python -m sapl highlight examples/basic.sapl --theme light

# Explore alternative backends
python -m sapl compile examples/basic.sapl --target machine
python -m sapl compile examples/basic.sapl --target bytecode
python -m sapl compile examples/basic.sapl --target python
python -m sapl compile examples/language_targets.sapl --target assembly
python -m sapl compile examples/language_targets.sapl --target csharp
python -m sapl compile examples/language_targets.sapl --target php
python -m sapl compile examples/language_targets.sapl --target rust

# Inspect structure-aware compilation output
python -m sapl advanced-compile examples/basic.sapl --target python --json

# Analyse script structure without executing it
python -m sapl inspect examples/basic.sapl --json

# Execute ad-hoc snippets or preload scripts inside the interactive shell
python -m sapl shell --script examples/basic.sapl --execute "NOTE \"Ready\"" --json

# Manage the static website bundle
python -m sapl website --list
python -m sapl website --export ./public --overwrite

# Preview documentation using the bundled HTTP server
python -m sapl serve --directory examples --once

# Bootstrap an isolated tooling environment
python -m sapl venv .sapl-env --print-required

# Run SAPL-native tests
python -m sapl test examples --plugin-dir examples/plugins

# Execute a workflow with plugin-provided enrichers
python -m sapl run examples/plugins/enrichment.sapl --plugin-dir examples/plugins
```

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Platform Compatibility](docs/PLATFORM_COMPATIBILITY.md)
- [Compilation From Source](docs/COMPILATION_FROM_SOURCE.md)
- [GUI and CLI Application Packaging](docs/GUI_AND_CLI_COMPILATION.md)
- [Plugin Development](docs/PLUGINS.md)
- [Core Syntax Overview](docs/CORE_SYNTAX_OVERVIEW.md)
- [Readability & Style Guide](docs/READABILITY_AND_STYLE.md)
- [Blue Teaming Playbooks](docs/BLUETEAMING.md)
- [Red Teaming Campaigns](docs/REDTEAMING.md)
- [Purple Teaming Exercises](docs/PURPLE_TEAMING.md)
- [Testing With `sapl-test`](docs/TESTING.md)
- [Performance Tips](docs/PERFORMANCE.md)
- [Maintainability Guidelines](docs/MAINTAINABILITY.md)
- [IDE Integration](docs/IDE_INTEGRATION.md)
- [Creating Packages & Libraries](docs/PACKAGING.md)
- [Modules & Packages](docs/MODULES_AND_PACKAGES.md)
- [Embedded Asset Bundling](docs/EMBEDDED_ASSETS.md)
- [Structured Codebase Walkthrough](docs/STRUCTURED_CODEBASE.md)
- [Regex Helper Overview](docs/REGEX.md)
- [Polyglot Compilation Targets](docs/LANGUAGE_TARGETS.md)
- [Language Target Field Guide](docs/POLYGLOT_LANGUAGES.md)
- [Example Gallery](docs/EXAMPLES.md)
- [Data Structures Guide](docs/DATA_STRUCTURES.md)
- [Functions & Async Patterns](docs/FUNCTIONS_AND_ASYNC.md)
- [Input, Output & Files](docs/IO_AND_FILES.md)
- [Exception Handling](docs/EXCEPTION_HANDLING.md)
- [Objects & Classes](docs/OBJECTS_AND_CLASSES.md)
- [Comprehensive Knowledge Base](comprehensive_docs/INDEX.md)

The advanced static website is available under `website/`. Use `python -m sapl website --serve` for local previews or export the assets for CDN hosting.

## Example plan

```text
TARGET ["https://demo.cybertex.local", "https://api.cybertex.local"]
SCOPE ["demo.cybertex.local", "api.cybertex.local"]

IMPORT asyncio

SET analysts = ["riley", "morgan"]
SET service_ports = {80, 443, 8080}
SET credentials = ("analyst", "hunter2")
SET host_metadata = {"owner": "appsec", "priority": "high"}
SET recon_hosts = [host FOR host IN targets IF "api" IN host]
SET engagement_mode = "stealth" IF len(recon_hosts) < len(targets) ELSE "full"
SET summarise_profile = lambda profile, tag="core": profile["host"] + ":" + tag
ASYNC DEF fetch_profile(host):
    RETURN await asyncio.sleep(0, result={"host": host, "status": "online"})
SET host_profiles = [AWAIT fetch_profile(host) FOR host IN recon_hosts]
SET profile_summaries = [summarise_profile(profile) FOR profile IN host_profiles]
username, _ = credentials
owner = host_metadata["owner"]
PAYLOAD sql_injection = [
    "' OR '1'='1",
    "' UNION SELECT NULL--",
    "admin' --",
]

FOR host IN targets:
    TASK "Initial Recon for {host}":
        "Document exposed surfaces before deeper enumeration"
        OUTPUT "Recon kick-off for {host}"
        PORTSCAN service_ports TOOL "nmap -sV {host}"
        IF "api" IN host:
            NOTE "Target exposes API endpoints"
        NOTE "Stakeholder {owner} notified of scan window"
        NOTE "Profiles evaluated {profile_summaries}"
        HTTP GET "{host}/status" EXPECT 200

TASK "Input Fuzzing":
    "Exercise payload library against authenticated surface"
    NOTE "Authenticating as {username}"
    FUZZ "{target}/search?q=" METHOD GET USING sql_injection
    FINDING medium "Potential SQLi vectors enumerated for {target}"

IF FALSE:
    INPUT "Override analyst handle: " AS analyst_override

SET report_name = "-".join(analysts)
RUN "whatweb {target}" SAVE AS fingerprint
REPORT "reports/{report_name}-findings.md"
```

Running the playbook above builds a structured execution plan, interpolating variables across tasks and actions while maintaining a full audit trail of findings, notes, payloads, and generated artifacts.

For a hands-on tour of the extended helper catalogue, see `examples/extended_features.sapl`, which walks through conversions, object inspection, string helpers, file IO, and custom exception handling in one self-contained script. To experiment with embedded multi-language assets and metadata aware packaging, start with `examples/embedding_demo.sapl`.

For a multi-module walkthrough covering inheritance, encapsulation, and
package-driven reuse, execute `examples/structured_project/main.sapl`.

Pair `examples/blueteam_operations.sapl` with `examples/redteam_operations.sapl` to rehearse purple-team collaboration scenarios across defensive and offensive workflows.

Explore the new targeted guides:

- `examples/data_structures_walkthrough.sapl` for lists, tuples, dictionaries,
  sets, and comprehensions with block comments.
- `examples/control_flow_showcase.sapl` for branching, looping, and exception
  handling patterns.
- `examples/async_patterns.sapl` for coroutine orchestration and lambda
  helpers.
- `examples/io_and_comments.sapl` for interactive IO and file persistence
  workflows.
- `examples/object_modeling.sapl` for inheritance, encapsulation, and
  polymorphic execution across blue, red, and purple teams.

## Core language features

### 1. Basic syntax & structure

- Indentation defines blocks – no braces required, though braces remain available for legacy scripts.
- Dynamic typing with runtime type promotion and string interpolation via `{placeholder}` formatting.
- Interpreted execution through `sapl.runtime.Interpreter`, or alternative backends when compiled.
- Multiple paradigms supported: procedural scripting for tasks, functional helpers via `DEF`, and object-oriented modelling with `CLASS` definitions.
- Documentation strings (`"doc"`) captured as the first statement inside tasks, functions, and classes, plus `#` single-line comments for inline context.

### 2. Built-in data types

| Category | Examples |
| --- | --- |
| Simple types | `int`, `float`, `bool`, `str`, `None` |
| Sequence types | Lists (`[1, 2]`), tuples (`(x, y)`), strings, iterators |
| Binary types | Bytes & bytearray via exposed Python built-ins |
| Collection types | Dictionaries (`{"key": value}`), sets (`{1, 2, 3}`) |

Multiple assignment mirrors Python’s destructuring semantics, so statements such as `username, _ = credentials` or `[left, right] = pair` split iterable values into individual bindings.

List comprehensions offer a compact way to derive new collections, for example `SET recon = [host FOR host IN targets IF "api" IN host]` filters scoped targets without leaking the loop variable outside the expression.

### 3. Built-in functions (87+)

SAPL exposes 90 curated built-ins including common Python functions (`abs`, `round`, `print`, `open`, `zip`), asynchronous helpers (`aiter`, `anext`), numerical utilities (`math_hypot`, `math_prod`, `math_factorial`), statistics helpers (`stats_mean`, `stats_geometric_mean`, `stats_variance`), randomisation and cryptography helpers (`random_choice`, `random_uniform`, `secret_token_hex`), URL tooling (`url_parse`, `url_join`, `url_encode`), text processing (`text_dedent`, `text_indent`), and filesystem shortcuts (`path_exists`, `path_read_text`, `path_write_text`, `path_glob`, `path_resolve`).

### 4. Operators

- Arithmetic: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`, `IN`
- Logical: `AND`, `OR`, `NOT`
- Augmented assignments: `+=`, `-=`, `*=`, `/=`, `//=`, `%=`, `**=`

### 5. Control flow statements

- `IF` / `ELIF` / `ELSE`
- `WHILE` with optional `ELSE`
- `FOR` loops over any iterable
- `BREAK` and `CONTINUE`
- `TRY` / `EXCEPT` / `ELSE` / `FINALLY`
- `RAISE` for signalling runtime failures
- Conditional expressions with `value IF condition ELSE other` for inline decisions

### 6. Function features

- `DEF` introduces dynamically scoped functions with default parameters and first-class support.
- Functions may be returned, passed as arguments, or stored in variables.
- Returning without a value yields `None`.
- Closures capture the lexical environment at definition time.
- A leading string literal becomes the function docstring, mirrored onto bound methods and available at runtime.
- `lambda` expressions build lightweight closures for inline data transformation.
- `ASYNC DEF` declares asynchronous routines that can `AWAIT` coroutines or asynchronous SAPL functions.

### 7. Object-oriented programming

- `CLASS` definitions create Python-compatible classes (backed by `type`).
- Methods are defined with `DEF` inside the class body and bind automatically to instances.
- Inheritance via `CLASS Derived(BaseOne, BaseTwo): ...`.
- Instances interact seamlessly with context managers and the interpreter environment.
- Docstrings placed as the first statement inside the class body populate `__doc__` for downstream tooling.

### 8. Error handling

- `TRY` blocks support multiple `EXCEPT` handlers with aliases, optional `ELSE`, and `FINALLY` suites.
- `RAISE` re-throws explicit exceptions.
- Linter diagnostics surface misuse such as `BREAK` outside loops or undefined identifiers.

### 9. Context managers

- `WITH` integrates with any object providing `__enter__` / `__exit__` – use Python built-ins (e.g., `open`) or custom classes.
- Aliases introduced with `AS` live for the duration of the block.

### 10. Modules and packages

- `IMPORT module [AS alias]` for whitelisted modules.
- `FROM module IMPORT name [AS alias]` and `FROM module IMPORT *` within the curated catalogue.
- Imported modules are tracked in the execution context and available to subsequent statements.

### 11. Input & output

- `OUTPUT expression` evaluates the argument (including placeholder interpolation) and prints it while recording an `output` action in the execution plan.
- `INPUT [prompt] AS name` optionally evaluates a prompt expression and captures interactive input into `name`, emitting an `input` action and storing the value for later reuse.
- Wrapping `INPUT` in conditional guards (e.g. `IF FALSE:`) allows non-interactive examples while keeping the syntax visible for operators.

### 12. Data conversion & object insight

- Helper functions such as `to_int`, `to_float`, `to_bool`, `to_list`, `to_tuple`, `to_set`, and `to_bytes` simplify adapting data sourced from payloads or IO.
- Object inspectors (`object_describe`, `object_members`, `object_public_attrs`, `object_methods`) surface metadata, attribute lists, and docstrings for any runtime object, making interactive debugging or report generation straightforward.

### 13. Functional & string helpers

- `compose` and `pipe` enable expressive data pipelines; `map_list`, `filter_list`, `flatten`, and `reduce` mirror the Python toolbox but eagerly materialise results for convenient reuse.
- String utilities (`string_upper`, `string_lower`, `string_title`, `string_strip`, `string_replace`, `string_split`, `string_join`, `string_pad_left`, `string_pad_right`, etc.) provide ergonomic one-liners for cleaning or formatting engagement data.

### 14. File utilities & exception ergonomics

- `file_read_text`, `file_write_text`, `file_append_text`, `file_read_bytes`, and `file_write_bytes` wrap common file workflows while honouring encodings.
- `define_exception`, `ensure_exception`, `raise_message`, and `rethrow` make it easy to craft bespoke exception hierarchies or propagate errors through `TRY`/`EXCEPT`/`FINALLY` suites.

## Standard library catalogue

`sapl.stdlib.STANDARD_LIBRARY_CATALOG` exposes category-to-module mappings covering the most common operational needs:

| Category | Modules |
| --- | --- |
| Core & OS services | `os`, `sys`, `pathlib`, `platform`, `logging`, `subprocess` |
| File & directory access | `pathlib`, `shutil`, `tempfile`, `glob` |
| Data persistence | `json`, `sqlite3`, `configparser`, `csv`, `pickle` |
| Data types & mathematics | `math`, `statistics`, `decimal`, `fractions`, `itertools`, `functools` |
| Networking & internet | `ipaddress`, `socket`, `ssl`, `http.client`, `urllib.parse`, `urllib.request` |
| Concurrent execution | `asyncio`, `threading`, `multiprocessing`, `concurrent.futures` |
| Development tools | `inspect`, `dataclasses`, `typing`, `pprint` |
| Text processing | `re`, `textwrap`, `difflib`, `string`, `html`, `xml.etree.ElementTree` |
| Exclusive features | `secrets`, `hashlib`, `hmac`, `uuid`, `zipfile`, `tarfile` |

Aliases such as `core.os`, `network.http`, or `security.hashlib` map to their underlying modules, and every module’s public names can be enumerated via `module_public_names`.

## Advanced tooling additions

- **Structure-aware compiler** – `sapl.advanced_compiler.AdvancedCompiler` and the
  `advanced-compile` CLI surface metadata for imports, classes, methods, tasks,
  and payloads alongside the compiled payload.
- **Embedded HTTP server** – `python -m sapl serve` runs a
  `http.server`-style preview server with optional `--once` behaviour for tests.
- **Package-friendly module loader** – `.sapl` modules within the project tree
  are imported directly, enabling reusable packages such as the
  `examples/structured_project/sapl_ops` helpers.
- **Virtual environment bootstrapper** – `python -m sapl venv` invokes
  `sapl.environment.create_virtual_environment` and copies the
  `sapl-required.yaml` manifest, which is also consumable via
  `sapl.load_required_config()`.

## Memory model

- A stack of frames stores variable scopes; global variables are preserved for execution summaries.
- Built-in identifiers live in a dedicated immutable mapping so user variables never shadow core functionality unintentionally.
- The runtime exposes a structured result containing targets, payloads, variables, notes, actions, findings, and final report destinations for downstream automation.

## Backends

| Backend | Description |
| --- | --- |
| Interpreter | Default runtime with dynamic evaluation, task orchestration, and rich execution results. |
| Machine code compiler | Emits pseudo-assembly instructions (`LOAD_CONST`, `STORE_NAME`, etc.) for analysis and documentation. |
| Bytecode compiler & VM | Generates a compact stack-based instruction stream executed by `sapl.backends.VirtualMachine`. |
| Transpiler | Produces readable Python source for integration with bespoke automation or scheduling systems. |

## Development

```bash
pip install pytest
pytest
```

No external dependencies are required beyond the Python standard library; every subsystem is implemented in pure Python.
