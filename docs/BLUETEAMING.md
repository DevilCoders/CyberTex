# Blue Teaming With SAPL

SAPL now exposes a dedicated helper set for defensive teams so that monitoring
and response playbooks can be modelled alongside offensive engagements.

## Event capture

Use the `blueteam_log_event` helper to generate structured telemetry from
scripts. Events normalise optional fields so they can be serialised straight to
JSON, forwarded to SIEM tooling, or attached to reports.

```sapl
SET alert = blueteam_log_event(
    "Suspicious lateral movement detected",
    severity="high",
    source="edr-sensor",
    tags=["lateral", "east-wing"],
    context={"host": "app-01", "process": "psexec"},
)
NOTE "Alert queued: {alert['description']} ({alert['severity']})"
```

## Response playbooks

`blueteam_playbook` packages response steps and objectives in a consistent
format. Pair the helper with SAPL’s reporting facilities to create living
runbooks that evolve with each exercise.

```sapl
SET containment = blueteam_playbook(
    "Ransomware containment",
    steps=[
        "Isolate affected hosts",
        "Block hash at endpoint protection",
        "Notify stakeholders",
    ],
    objectives=["restore service", "limit spread"],
)
REPORT "reports/blueteam.md" USING containment
```

## Readiness snapshots

For tabletop exercises or automated metrics collection, call
`blueteam_readiness(score, indicators)` to publish a normalised readiness score
between `0.0` and `1.0`.

```sapl
SET readiness = blueteam_readiness(0.82, ["tested IR plan", "auto patching"])
NOTE "Current defensive readiness: {readiness['score']}"
```

## Combined workflows

These helpers are available across interpreters, compilers, the linter, and the
`sapl-test` harness. Defensive teams can therefore record detections,
link them to runbooks, and export reports without leaving the SAPL ecosystem.

See `examples/blueteam_response.sapl` for an automation-heavy containment workflow that embeds SQL, Python, and reporting assets alongside SOC actions.
