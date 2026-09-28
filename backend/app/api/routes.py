from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
import httpx

from app.config import settings
from app.demo import demo_store
from app.schemas import AssessmentRequest, WeatherRangeQuery

router = APIRouter()

def icao_or_404(icao: str):
    airport = demo_store.airport(icao)
    if not airport:
        raise HTTPException(status_code=404, detail="Aeropuerto no encontrado en la fuente configurada")
    return airport

@router.get("/airports/{icao}")
def airport(icao: str):
    return icao_or_404(icao)

@router.get("/airports/{icao}/runways")
def runways(icao: str):
    icao_or_404(icao)
    return {"airport_icao": icao.upper(), "items": demo_store.runways(icao)}

@router.get("/airports/{icao}/taxiways")
def taxiways(icao: str):
    icao_or_404(icao)
    return {"airport_icao": icao.upper(), "items": demo_store.taxiways(icao)}

@router.get("/airports/{icao}/notams/live")
async def live_notams(icao: str):
    icao_or_404(icao)
    if settings.demo_mode:
        return {"airport_icao": icao.upper(), "source": "FAA", "retrieved_at": datetime.now(timezone.utc), "status": "DEMO_NO_EXTERNAL_CALL", "items": []}
    return {"airport_icao": icao.upper(), "source": "FAA", "status": "PROVIDER_NOT_CONFIGURED", "items": []}

@router.get("/airports/{icao}/weather/current")
async def current_weather(icao: str):
    icao_or_404(icao)
    if settings.demo_mode:
        return {"airport_icao": icao.upper(), "source": "AWC", "status": "DEMO_NO_EXTERNAL_CALL", "observations": []}
    return {"airport_icao": icao.upper(), "source": "AWC", "status": "PROVIDER_NOT_CONFIGURED", "observations": []}

@router.get("/airports/{icao}/weather/range")
async def weather_range(icao: str, hours: int = Query(24, ge=1, le=168), temperature_min_c: float | None = None, temperature_max_c: float | None = None, qnh_min_hpa: float | None = None, qnh_max_hpa: float | None = None, minimum_observations: int = Query(1, ge=1)):
    icao_or_404(icao)
    return {"airport_icao": icao.upper(), "status": "DATA_INSUFFICIENT", "hours": hours, "minimum_observations": minimum_observations, "temperature_range": {"configured_min_c": temperature_min_c, "configured_max_c": temperature_max_c}, "qnh_range": {"configured_min_hpa": qnh_min_hpa, "configured_max_hpa": qnh_max_hpa}, "observations": [], "message": "No hay histórico METAR local; la consulta on-demand del proveedor aún no entregó observaciones."}

@router.post("/assessments")
def create_assessment(request: AssessmentRequest):
    try:
        return demo_store.evaluate(request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.get("/assessments/{assessment_id}")
def get_assessment(assessment_id: str):
    assessment = demo_store.assessments.get(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return assessment

@router.post("/ingestion/documents")
def register_document(document: dict):
    required = {"source_code", "document_type", "status"}
    missing = required - document.keys()
    if missing:
        raise HTTPException(status_code=422, detail=f"Faltan campos: {sorted(missing)}")
    if document["status"] not in {"DISCOVERED", "DOWNLOADED", "HASHED", "VALIDATION_PENDING", "REVIEW_REQUIRED", "APPROVED", "PUBLISHED", "REJECTED"}:
        raise HTTPException(status_code=422, detail="Estado de documento no válido")
    document["registered_at"] = datetime.now(timezone.utc).isoformat()
    demo_store.documents.append(document)
    return {"status": "registered", "document": document}
