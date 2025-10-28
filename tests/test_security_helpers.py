from sapl.stdlib.extended import EXTRA_FUNCTIONS


def test_blueteam_helpers_normalise_optional_fields():
    log_event = EXTRA_FUNCTIONS["blueteam_log_event"]
    readiness = EXTRA_FUNCTIONS["blueteam_readiness"]
    event = log_event("Investigate beacon")
    assert event["source"] == "runtime"
    assert event["tags"] == []
    readiness_snapshot = readiness(1.4, ["patched"])
    assert readiness_snapshot["score"] == 1.0
    assert readiness_snapshot["indicators"] == ["patched"]


def test_redteam_helpers_return_structured_payloads():
    objective = EXTRA_FUNCTIONS["redteam_objective"](
        "Establish foothold",
        tactics=["TA0001"],
    )
    campaign = EXTRA_FUNCTIONS["redteam_campaign"](
        "Test",
        [objective],
        operators=["pat"],
    )
    matrix = EXTRA_FUNCTIONS["redteam_emulation_matrix"]({"TA0001": ["T1059"]})
    assert campaign["objectives"][0]["name"] == "Establish foothold"
    assert campaign["operators"] == ["pat"]
    assert matrix["mapping"]["TA0001"] == ["T1059"]


def test_purpleteam_helpers_merge_red_and_blue():
    alignment = EXTRA_FUNCTIONS["purpleteam_alignment"](
        campaign={"title": "Assessment"},
        readiness={"score": 0.7},
        shared_metrics=["mean-time-detect"],
    )
    exercise = EXTRA_FUNCTIONS["purpleteam_exercise_plan"](
        "Purple drill",
        objectives=[{"name": "Detect beacon"}],
        detections=[{"name": "Sysmon"}],
        outcomes=["Improved visibility"],
    )
    scorecard = EXTRA_FUNCTIONS["purpleteam_scorecard"](
        alignment=alignment,
        exercise=exercise,
        maturity=1.4,
        notes=["Monthly review"],
    )
    assert alignment["metrics"] == ["mean-time-detect"]
    assert exercise["type"] == "purpleteam_exercise"
    assert scorecard["maturity"] == 1.0
    assert scorecard["notes"] == ["Monthly review"]
