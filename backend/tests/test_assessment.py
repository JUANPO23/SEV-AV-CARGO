from app.demo import demo_store
from app.schemas import AssessmentRequest

def test_runway_rules_and_assessment():
    result = demo_store.evaluate(AssessmentRequest(airport_icao="SKUC", selected_runway="11"))
    assert result.status in {"NOT_VIABLE_FROM_INFRASTRUCTURE", "CONDITIONAL"}
    assert any(x.rule_code == "RUNWAY.LENGTH.MINIMUM" for x in result.validations)

def test_unknown_airport():
    try:
        demo_store.evaluate(AssessmentRequest(airport_icao="ZZZZ"))
    except ValueError as exc:
        assert "Aeropuerto" in str(exc)
    else:
        raise AssertionError("Expected unknown airport")
