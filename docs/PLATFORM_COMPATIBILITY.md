# Platform Compatibility

SAPL is implemented in pure Python and runs consistently across Linux, macOS, and Windows. The following sections highlight platform-specific considerations.

## Linux

* Full feature set supported, including async workflows and the HTTP server.
* Ideal for automation pipelines and containerised deployments.
* Ensure UTF-8 locales are configured to avoid encoding issues in highlighted output.
* `sapl server --systemd` emits unit files for managed services.

## macOS

* Fully supported when running under the system Python or Homebrew Python.
* Install the Xcode Command Line Tools to ensure optional native dependencies compile when required.
* Launch the HTTP server using `sapl server --bind 127.0.0.1 --port 8000` for local testing.
* Use `sapl env create --python /usr/local/bin/python3` to avoid conflicts with
  the system Python.

## Windows

* Compatible with PowerShell and Windows Terminal. Use the `sapl` and `sapl-test`
  entry points provided by the installer or virtual environment.
* When creating virtual environments, activate them using `.\.venv\Scripts\Activate.ps1`.
* File watching and background server tooling integrate with Windows Firewall prompts; allow inbound requests when prompted.
* The advanced compiler produces signed executables when `--signing-profile` is
  configured in `required.yaml`.

## Cross-Platform Projects

* Use the `sapl environment` helpers to generate consistent virtual environments regardless of platform.
* Document OS-specific setup steps inside your project README, referencing `docs/INSTALLATION.md` for detailed commands.
* Include platform-specific CI jobs (for example GitHub Actions matrices) to validate cross-platform operation.
* When embedding SAPL in other languages, reference the bindings listed in
  [POLYGLOT_LANGUAGES.md](POLYGLOT_LANGUAGES.md) to select the best API for each
  operating system.

## Character Encoding

* SAPL assumes UTF-8 encoded source files. Ensure your editor and version control system preserve UTF-8 encoding.
* CLI output respects the terminal encoding; on Windows set `chcp 65001` when using legacy consoles.

## File Paths

* The module loader normalises paths using `Path.resolve()`, ensuring forward slashes are accepted on every platform.
* When referencing files in scripts, prefer POSIX-style paths (`reports/findings.md`) for portability.
