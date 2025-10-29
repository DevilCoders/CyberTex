# SAPL Installation Guide

This guide walks through installing SAPL on the three primary desktop operating systems. Each section assumes you have cloned or downloaded the CyberTex repository.

## Common Prerequisites

* Python 3.11 or newer.
* Git (optional but recommended for keeping the toolkit updated).
* A C compiler when building native extensions for plugins or tooling.

All examples use a shell prompt. Replace paths with your own directories as needed.

## Windows

1. Install Python from [python.org](https://www.python.org/downloads/windows/) and ensure the **Add Python to PATH** option is checked.
2. Open *Windows Terminal* or *PowerShell* and clone the repository:
   ```powershell
   git clone https://example.com/CyberTex.git
   cd CyberTex
   ```
3. Create a virtual environment and activate it:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies listed in `required.yaml` using the SAPL CLI:
   ```powershell
   sapl env create
   sapl env sync
   ```
5. Verify the installation and optional subcommands:
   ```powershell
   sapl --help
   sapl-test --help
   ```

## Linux

1. Install Python using your package manager (for example `sudo apt install python3 python3-venv`).
2. Clone the repository:
   ```bash
   git clone https://example.com/CyberTex.git
   cd CyberTex
   ```
3. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   sapl env create
   sapl env sync
   ```
5. Run the CLI to confirm the installation:
   ```bash
   sapl --help
   sapl compile --help
   ```

## macOS

1. Install Python 3.11+ via [Homebrew](https://brew.sh/) or the official installer.
2. Open Terminal and clone the repository:
   ```bash
   git clone https://example.com/CyberTex.git
   cd CyberTex
   ```
3. Create a virtual environment using the Homebrew Python binary if present:
   ```bash
   /usr/local/bin/python3 -m venv .venv
   source .venv/bin/activate
   ```
4. Install runtime dependencies:
   ```bash
   sapl env create
   sapl env sync
   ```
5. Run the CLI help to confirm:
   ```bash
   sapl --help
   sapl website --help
   ```

## Troubleshooting Tips

* On Windows, ensure the terminal is opened *after* installing Python so the PATH changes take effect.
* When using corporate proxies, configure `pip` or the `SAPL_INDEX_URL` environment variable before installing.
* If the optional native backends fail to compile, install build tools such as *Build Tools for Visual Studio* (Windows) or Xcode Command Line Tools (macOS).
* Refer to [SAPL_ENVIRONMENTS.md](SAPL_ENVIRONMENTS.md) for advanced environment
  management, including offline mirrors and per-team profiles.
