# Purple Teaming with SAPL

SAPL now ships with first-class purple-teaming helpers that blend the existing
blue- and red-team primitives into cohesive collaboration artefacts.

## Alignment Snapshots

Use `purpleteam_alignment` to combine a red-team campaign with the latest blue
readiness snapshot. The helper normalises shared metrics, documents cadence, and
returns a dictionary that can be exported into reporting systems or shared with
stakeholders.

```sapl
IMPORT sapl.stdlib.extended AS helpers

alignment = helpers.purpleteam_alignment(
    campaign=helpers.redteam_campaign("Purple Push", [objective]),
    readiness=helpers.blueteam_readiness(0.72, ["EDR coverage", "Playbook" ]),
    shared_metrics=["mean-time-detect", "containment-lag"],
    cadence="quarterly",
)
```

## Exercise Plans

`purpleteam_exercise_plan` describes the joint exercise, listing objectives,
detections to validate, facilitation roles, and the desired outcomes. The return
value is a serialisable dictionary, making it easy to persist the plan or
expose it via the reporting helpers built into the runtime.

## Scorecards

When an exercise concludes, call `purpleteam_scorecard` to wrap the alignment
context, exercise description, and a maturity score. The helper bounds the score
to the `[0, 1]` range so dashboards remain consistent.

```sapl
scorecard = helpers.purpleteam_scorecard(
    alignment=alignment,
    exercise=exercise,
    maturity=0.94,
    notes=["Improve analytics", "Automate runbook triggers"],
)
```

The purple-team helpers integrate seamlessly with the documentation and
reporting pipelines introduced earlier, making it simple to expand existing
playbooks into collaborative purple exercises.
