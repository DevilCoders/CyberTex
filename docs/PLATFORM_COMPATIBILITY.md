# Platform Compatibility

SAPL is implemented in pure Python and runs consistently across Linux, macOS, and Windows. The following sections highlight platform-specific considerations.

## Linux

* Full feature set supported, including async workflows and the HTTP server.
* Ideal for automation pipelines and containerised deployments.
* Ensure UTF-8 locales are configured to avoid encoding issues in highlighted output.

## macOS

* Fully supported when running under the system Python or Homebrew Python.
* Install the Xcode Command Line Tools to ensure optional native dependencies compile when required.
* Launch the HTTP server using `python -m sapl serve --bind 127.0.0.1 --port 8000` for local testing.

## Windows

* Compatible with PowerShell and Windows Terminal. Use `py -m sapl` or `python -m sapl` depending on your Python installation.
* When creating virtual environments, activate them using `.\.venv\Scripts\Activate.ps1`.
* File watching and background server tooling integrate with Windows Firewall prompts; allow inbound requests when prompted.

## Cross-Platform Projects

* Use the `sapl environment` helpers to generate consistent virtual environments regardless of platform.
* Document OS-specific setup steps inside your project README, referencing `docs/INSTALLATION.md` for detailed commands.
* Include platform-specific CI jobs (for example GitHub Actions matrices) to validate cross-platform operation.

## Character Encoding

* SAPL assumes UTF-8 encoded source files. Ensure your editor and version control system preserve UTF-8 encoding.
* CLI output respects the terminal encoding; on Windows set `chcp 65001` when using legacy consoles.

## File Paths

* The module loader normalises paths using `Path.resolve()`, ensuring forward slashes are accepted on every platform.
* When referencing files in scripts, prefer POSIX-style paths (`reports/findings.md`) for portability.
