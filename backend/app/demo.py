from datetime import datetime, timezone
from uuid import uuid4
from .schemas import *
from .pavement import evaluate_pcn, parse_pcn

AIRCRAFT = AircraftProfile()

DEMO_AIRPORT = Airport(icao="SKUC", iata="AUC", name="Aeropuerto Santiago Pérez Quiroz", location="Arauca, Colombia", elevation_ft=423)
DEMO_RUNWAYS = [
    Runway(designator="11", length_m=2100, width_m=30, surface="ASPHALT", pavement=parse_pcn("PCN 81/F/B/X/T")),
    Runway(designator="29", length_m=2100, width_m=30, surface="ASPHALT", pavement=parse_pcn("PCN 81/F/B/X/T")),
]
DEMO_TAXIWAYS = [
    Taxiway(designator=x, width_m=25, surface="ASPHALT", pavement=parse_pcn("PCN 81/F/B/X/T"), restrictions=[]) for x in ["A", "B", "C", "D"]
]

class DemoStore:
    def __init__(self):
        self.assessments: dict[str, Assessment] = {}
        self.documents: list[dict] = []

    def airport(self, icao: str) -> Airport | None:
        return DEMO_AIRPORT if icao.upper() == "SKUC" else None

    def runways(self, icao: str) -> list[Runway]:
        return DEMO_RUNWAYS if icao.upper() == "SKUC" else []

    def taxiways(self, icao: str) -> list[Taxiway]:
        return DEMO_TAXIWAYS if icao.upper() == "SKUC" else []

    def evaluate(self, request: AssessmentRequest) -> Assessment:
        airport = self.airport(request.airport_icao)
        if not airport:
            raise ValueError("Aeropuerto no encontrado")
        validations: list[ValidationResult] = []
        runways = self.runways(request.airport_icao)
        selected = next((r for r in runways if r.designator == request.selected_runway), runways[0] if runways else None)
        if not selected:
            validations.append(ValidationResult(rule_code="RUNWAY.MISSING", status="DATA_INSUFFICIENT", severity="BLOCKING", message="No hay pistas publicadas."))
        else:
            if selected.length_m is None:
                validations.append(ValidationResult(rule_code="RUNWAY.LENGTH.MISSING", status="DATA_INSUFFICIENT", severity="BLOCKING", message="Falta longitud de pista."))
            elif selected.length_m < AIRCRAFT.minimum_runway_length_m:
                validations.append(ValidationResult(rule_code="RUNWAY.LENGTH.MINIMUM", status="BLOCKING", severity="BLOCKING", actual_value=selected.length_m, required_value=1400, message="La pista no cumple los 1400 m mínimos."))
            else:
                validations.append(ValidationResult(rule_code="RUNWAY.LENGTH.MINIMUM", status="PASS", actual_value=selected.length_m, required_value=1400, message="La longitud cumple."))
            if selected.width_m is None:
                validations.append(ValidationResult(rule_code="RUNWAY.WIDTH.MISSING", status="DATA_INSUFFICIENT", severity="BLOCKING", message="Falta ancho de pista."))
            elif selected.width_m < AIRCRAFT.minimum_runway_width_m:
                validations.append(ValidationResult(rule_code="RUNWAY.WIDTH.MINIMUM", status="BLOCKING", severity="BLOCKING", actual_value=selected.width_m, required_value=44, message="La pista no cumple los 44 m mínimos."))
            else:
                validations.append(ValidationResult(rule_code="RUNWAY.WIDTH.MINIMUM", status="PASS", actual_value=selected.width_m, required_value=44, message="El ancho cumple."))
            if selected.pavement:
                p = evaluate_pcn(AIRCRAFT, selected.pavement, request.aircraft_mass_kg)
                validations.append(ValidationResult(rule_code="PAVEMENT.ACN_PCN", status=p["status"], severity=p["severity"], actual_value=p.get("acn"), required_value=p.get("pcn"), message=p["message"]))
        blocking = any(v.severity == "BLOCKING" and v.status in {"BLOCKING", "FAIL", "DATA_INSUFFICIENT"} for v in validations)
        insufficient = any(v.status == "DATA_INSUFFICIENT" for v in validations)
        warning = any(v.status == "WARNING" for v in validations)
        status = "DATA_INSUFFICIENT" if insufficient else "NOT_VIABLE_FROM_INFRASTRUCTURE" if blocking else "CONDITIONAL" if warning else "VIABLE_FROM_INFRASTRUCTURE"
        assessment = Assessment(id=str(uuid4()), airport_icao=request.airport_icao, status=status, validations=validations, snapshots={"aircraft": AIRCRAFT.model_dump(), "runway": selected.model_dump() if selected else None, "rule_version": "1.0.0"})
        self.assessments[assessment.id] = assessment
        return assessment

demo_store = DemoStore()
