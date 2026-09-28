from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.auth import current_actor
from app.db import AssessmentModel, AuditEventModel, AirportModel, FieldProvenanceModel, SourceDocumentModel, ValidationResultModel, get_db
from app.demo import demo_store
from app.providers import AwcMetarClient, FaaNotamClient, ProviderError
from app.schemas import AssessmentRequest
from app.weather import evaluate_weather_range

router = APIRouter()

def airport_or_404(icao: str, db: Session):
    normalized = icao.upper().strip()
    found = db.query(AirportModel).filter_by(icao=normalized).first()
    if found:
        return found
    airport = demo_store.airport(normalized)
    if airport:
        return airport
    raise HTTPException(status_code=404, detail="Aeropuerto no encontrado")

@router.get("/airports/{icao}")
def airport(icao: str, db: Session = Depends(get_db)):
    item = airport_or_404(icao, db)
    return item if isinstance(item, dict) else (item.__dict__ if isinstance(item, AirportModel) else item)

@router.get("/airports/{icao}/runways")
def runways(icao: str, db: Session = Depends(get_db)):
    item = airport_or_404(icao, db)
    if isinstance(item, AirportModel): return {"airport_icao": item.icao, "items": [x.__dict__ for x in item.runways]}
    return {"airport_icao": icao.upper(), "items": demo_store.runways(icao)}

@router.get("/airports/{icao}/taxiways")
def taxiways(icao: str, db: Session = Depends(get_db)):
    item = airport_or_404(icao, db)
    if isinstance(item, AirportModel): return {"airport_icao": item.icao, "items": [x.__dict__ for x in item.taxiways]}
    return {"airport_icao": icao.upper(), "items": demo_store.taxiways(icao)}

@router.get("/airports/{icao}/notams/live")
async def live_notams(icao: str, db: Session = Depends(get_db), actor: str = Depends(current_actor)):
    airport_or_404(icao, db)
    try: items = await FaaNotamClient().search(icao)
    except ProviderError as exc: raise HTTPException(status_code=502, detail=str(exc)) from exc
    for item in items: db.add(AuditEventModel(actor=actor, action="LIVE_NOTAM_QUERY", resource_type="airport", resource_id=icao.upper(), payload=item.model_dump(mode="json")))
    db.commit()
    return {"airport_icao": icao.upper(), "source": "FAA", "retrieved_at": datetime.now(timezone.utc), "status": "SUCCESS" if not settings_demo() else "DEMO_NO_EXTERNAL_CALL", "items": items}

def settings_demo():
    from app.config import settings
    return settings.demo_mode

@router.get("/airports/{icao}/weather/current")
async def current_weather(icao: str, db: Session = Depends(get_db), actor: str = Depends(current_actor)):
    airport_or_404(icao, db)
    try: items = await AwcMetarClient().search(icao, hours=2)
    except ProviderError as exc: raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"airport_icao": icao.upper(), "source": "AWC", "status": "SUCCESS" if items else "DATA_INSUFFICIENT", "observations": items}

@router.get("/airports/{icao}/weather/range")
async def weather_range(icao: str, hours: int = Query(24, ge=1, le=168), temperature_min_c: float | None = None, temperature_max_c: float | None = None, qnh_min_hpa: float | None = None, qnh_max_hpa: float | None = None, minimum_observations: int = Query(1, ge=1), db: Session = Depends(get_db)):
    airport_or_404(icao, db)
    try: observations = await AwcMetarClient().search(icao, hours=hours)
    except ProviderError as exc: raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"airport_icao": icao.upper(), **evaluate_weather_range(observations, temperature_min_c=temperature_min_c, temperature_max_c=temperature_max_c, qnh_min_hpa=qnh_min_hpa, qnh_max_hpa=qnh_max_hpa, minimum_observations=minimum_observations)}

@router.post("/assessments")
def create_assessment(request: AssessmentRequest, db: Session = Depends(get_db), actor: str = Depends(current_actor)):
    try: result = demo_store.evaluate(request)
    except ValueError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc
    model = AssessmentModel(id=result.id, airport_icao=result.airport_icao, status=result.status, created_by=actor, request_snapshot=request.model_dump(), result_snapshot=result.model_dump(mode="json"))
    db.add(model)
    for item in result.validations: db.add(ValidationResultModel(assessment_id=result.id, rule_code=item.rule_code, status=item.status, severity=item.severity, message=item.message, actual_value=item.actual_value, required_value=item.required_value, source_reference=item.source_reference))
    db.add(AuditEventModel(actor=actor, action="CREATE_ASSESSMENT", resource_type="assessment", resource_id=result.id, payload=request.model_dump()))
    db.commit()
    return result

@router.get("/assessments/{assessment_id}")
def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    item = db.query(AssessmentModel).filter_by(id=assessment_id).first()
    if item: return item.result_snapshot
    assessment = demo_store.assessments.get(assessment_id)
    if not assessment: raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return assessment

@router.post("/ingestion/documents")
def register_document(document: dict, db: Session = Depends(get_db), actor: str = Depends(current_actor)):
    allowed = {"DISCOVERED", "DOWNLOADED", "HASHED", "CLASSIFIED", "EXTRACTED", "NORMALIZED", "VALIDATION_PENDING", "REVIEW_REQUIRED", "APPROVED", "PUBLISHED", "SUPERSEDED", "REJECTED"}
    if not {"source_code", "document_type", "status"}.issubset(document): raise HTTPException(status_code=422, detail="source_code, document_type y status son obligatorios")
    if document["status"] not in allowed: raise HTTPException(status_code=422, detail="Estado de documento no válido")
    item = SourceDocumentModel(source_code=document["source_code"], document_type=document["document_type"], airport_icao=document.get("airport_icao"), revision=document.get("revision"), status=document["status"], document_url=document.get("document_url"), content_hash=document.get("content_hash"), parser_version=document.get("parser_version"), raw_metadata=document)
    db.add(item); db.flush(); db.add(AuditEventModel(actor=actor, action="REGISTER_AIP_DOCUMENT", resource_type="source_document", resource_id=str(item.id), payload=document)); db.commit(); db.refresh(item)
    return {"id": item.id, "status": item.status, "review_required": item.status in {"REVIEW_REQUIRED", "VALIDATION_PENDING"}}

@router.post("/ingestion/documents/{document_id}/review")
def review_document(document_id: int, decision: dict, db: Session = Depends(get_db), actor: str = Depends(current_actor)):
    item = db.query(SourceDocumentModel).filter_by(id=document_id).first()
    if not item: raise HTTPException(status_code=404, detail="Documento no encontrado")
    target = decision.get("status")
    if target not in {"APPROVED", "PUBLISHED", "REJECTED", "REVIEW_REQUIRED"}: raise HTTPException(status_code=422, detail="Decisión no válida")
    item.status = target; item.raw_metadata = {**(item.raw_metadata or {}), "review": decision, "reviewed_by": actor}
    db.add(AuditEventModel(actor=actor, action="REVIEW_AIP_DOCUMENT", resource_type="source_document", resource_id=str(document_id), payload=decision)); db.commit()
    return {"id": document_id, "status": target, "reviewed_by": actor}
