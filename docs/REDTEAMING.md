# Red Teaming With SAPL

Red team operators can leverage the new structured helpers to describe goals,
organise campaigns, and map detection coverage alongside blue-team telemetry.

## Objectives and tactics

`redteam_objective` records an engagement goal together with mapped tactics,
related detections, and expected impact. The output is safe for reporting or for
feeding into automation pipelines.

```sapl
SET lateral = redteam_objective(
    "Establish lateral movement",
    tactics=["TA0008", "TA0009"],
    detections=["SOC playbook 42", "EDR alert"],
    impact="credential theft",
)
NOTE "Objective planned: {lateral['name']}"
```

## Campaign design

Bundle multiple objectives together with `redteam_campaign`. You can attach the
operators involved and keep running notes for after-action reviews.

```sapl
SET campaign = redteam_campaign(
    "Quarterly purple-team exercise",
    [lateral],
    operators=["alex", "jules"],
    notes=["Coordinate with blue team prior to execution"],
)
REPORT "reports/redteam.md" USING campaign
```

## Emulation matrices

To mirror MITRE ATT&CK style matrices, supply the mapping of tactics to
techniques to `redteam_emulation_matrix`.

```sapl
SET matrix = redteam_emulation_matrix({"TA0002": ["T1059", "T1204"]})
OUTPUT matrix
```

## Collaboration with blue teams

Because the helpers sit inside the standard library catalogue they can be
combined with blue-team playbooks in a single script, making SAPL a natural
platform for purple-team exercises and capability benchmarking.

Reference `examples/redteam_operation.sapl` for an automation-ready playbook that pairs HTML, Python, and C++ embeds with campaign orchestration.
