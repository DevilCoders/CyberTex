# Classes, Objects, and Polymorphism

Object-oriented programming in SAPL enables reusable capability models across
blue, red, and purple team workflows.

## Class Basics

* `CLASS Name:` introduces a new class. Constructor logic lives inside `DEF __init__(self, ...)`.
* Attributes and methods use Python-style syntax. Use `self` to reference the
  instance.
* Docstrings on classes and methods improve inspector output and linter hints.

## Inheritance

* Define subclasses with `CLASS BlueRun(TaskPlan):` to share behaviour.
* Call `super().__init__()` for parent initialisation.
* Override methods to specialise behaviour; use `sapl.stdlib.extended` helpers to
  merge payloads or metrics.

## Encapsulation and Polymorphism

* Prefix internal helpers with `_` to communicate private intent.
* Provide consistent method signatures so polymorphic collections can iterate
  over tasks without branching.
* Combine with comprehension and lambda constructs to route events to the
  correct objects.

## Integration with Other Features

* Methods can be synchronous or async. Decorate them with plugins for logging or
  telemetry.
* The advanced compiler lifts class definitions into all language backends,
  including Python, C#, Java, and Rust, preserving inheritance hierarchies.

## Example

`examples/object_modeling.sapl` demonstrates classes coordinating blue, red, and
purple capabilities with shared base classes and per-team overrides.
