# Example Gallery

The `examples/` directory now contains a variety of workflows demonstrating advanced SAPL features.

## regex_workbench.sapl

Highlights the new regular-expression helpers by extracting indicators from sample log payloads and generating findings.

## cross_platform_deployment.sapl

Documents platform-aware deployment steps, emitting notes and tasks tailored for Linux, macOS, and Windows environments.

## gui_cli_builds.sapl

Shows how to plan GUI and CLI distribution pipelines, including compilation targets and packaging actions.

## advanced_compiler_pipeline.sapl

Runs the incremental compiler with optimisation profiles, publishes artifacts to
the SAPL server, and records diagnostics for later review.

## sapl_server_bootstrap.sapl

Configures TLS certificates, authenticated users, and hot-reload directories for
the built-in server before seeding the website bundle.

## cli_automation_suite.sapl

Automates `sapl fmt`, `sapl env sync`, `sapl-test`, and `sapl compile` to show
how the CLI streamlines day-to-day development.

## plugins/enrichment.sapl

Works with the Python plugin located in `examples/plugins/ip_enricher.py`, illustrating how plugin-provided built-ins enrich engagement data.

## blueteam_operations.sapl

Demonstrates the blue-team helper suite by logging detections, building readiness snapshots, and exporting SOC runbooks from one plan.

## redteam_operations.sapl

Pairs with the blue-team script to stage objectives, campaigns, and emulation matrices that feed into purple-team exercises.

## purpleteam_alignment.sapl

Demonstrates how the purple-team helpers can align campaigns, readiness, exercise plans, and scorecards into a single workflow.

## language_targets.sapl

Shows how to prepare a script that compiles cleanly into the assembly, C, C++,
C#, PHP, SQL, Go, Java, JavaScript, Perl, Rust, Ruby, and R emitters using the
refreshed CLI.

## data_structures_walkthrough.sapl

Tours list, tuple, dictionary, set, and comprehension features while
demonstrating the new multi-line `##` comment blocks and readability-focused
helpers.

## virtual_environment_management.sapl

Guides operators through creating, activating, and syncing virtual environments
across Linux, macOS, and Windows hosts.

## control_flow_showcase.sapl

Illustrates branching, loops, exception handling, async `AWAIT`, and the
interaction between flow control statements.

## async_patterns.sapl

Highlights coroutine definitions, lambda helpers, and list comprehensions in an
async status gathering scenario.

## io_and_comments.sapl

Demonstrates `INPUT`, `OUTPUT`, filesystem helpers, and block comments for
operator guidance.

## website_publishing_flow.sapl

Generates documentation, integrates sapl-test reports, and deploys to the SAPL
website preview server for stakeholder review.

## plugin_ci_pipeline.sapl

Runs plugin-specific tests, collects coverage, and publishes the package to an
internal index, illustrating maintainable extension workflows.

## object_modeling.sapl

Models inheritance, encapsulation, and polymorphism with base classes and per-
team overrides that integrate with the reporting helpers.

Use these scripts as templates when building your own SAPL projects.
