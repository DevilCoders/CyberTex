# Structured SAPL Project Example

This example demonstrates how to organise a SAPL codebase using packages and
modules. Run the entry point from this directory so local imports resolve
correctly:

```bash
python -m sapl run examples/structured_project/main.sapl
```

The project layout is intentionally similar to a Python package:

```
examples/structured_project/
├── main.sapl                # entry point
└── sapl_ops/                # reusable package
    ├── __init__.sapl        # package facade
    ├── entities.sapl        # class hierarchy with inheritance & polymorphism
    └── reports.sapl         # helper functions for summarising data
```

The runtime now resolves imports such as `IMPORT sapl_ops.entities` and handles
package initialisation automatically.
