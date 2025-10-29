# Building GUI and CLI Applications

SAPL targets cybersecurity automation, but compiled outputs can feed GUI or CLI front-ends. This document outlines strategies for packaging SAPL workflows into distributable applications.

## Command-Line Tools

1. Author your SAPL workflow under `scripts/`.
2. Transpile to Python:
   ```bash
   sapl compile scripts/scan.sapl --target python > build/scan.py
   ```
3. Wrap the generated Python inside a thin CLI harness using `argparse` or reuse
   `sapl.cli` utilities documented in [SAPL_CLI.md](SAPL_CLI.md).
4. Package the script as a standalone executable with tools such as `shiv`, `pex`, or `pyinstaller`.

## Graphical Applications

1. Transpile your SAPL workflow to Python or bytecode as above.
2. Import the generated module into a GUI toolkit (for example, PySide6, Tkinter, or Kivy).
3. Expose entry points that trigger SAPL functions when users interact with the interface. Example using PySide6:
   ```python
   from pathlib import Path
   from PySide6.QtWidgets import QApplication, QPushButton
   import transpiled_scan

   def run_scan():
       result = transpiled_scan.main()
       print(result)

   app = QApplication([])
   button = QPushButton("Run scan")
   button.clicked.connect(run_scan)
   button.show()
   app.exec()
   ```
4. Bundle the GUI using `pyinstaller` or platform-specific packaging tools.

## Hybrid Approaches

* Use `sapl server` to expose REST endpoints backed by SAPL workflows, then
  build desktop or web front-ends on top.
* Combine CLI and GUI entry points by sharing a compiled Python module.
* Integrate with the advanced website builder ([SAPL_WEBSITE.md](SAPL_WEBSITE.md))
  when you need both web dashboards and local GUI experiences.

## Distribution Tips

* Ship a configuration file describing the required Python version and dependencies. Reference `required.yaml` directly so
  consumers can recreate the environment.
* Automate builds via CI/CD pipelines, running `sapl-test` and linting before packaging.
* On Windows, sign executables to avoid SmartScreen warnings; on macOS, notarize the app bundle when distributing externally.
* Publish resulting artifacts via `sapl server` or the packaging workflow
  described in [PACKAGING.md](PACKAGING.md).
