from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field, field_validator

class Airport(BaseModel):
    icao: str
    iata: str | None = None
    name: str
    location: str | None = None
    elevation_ft: int | None = None
    source_status: str = "DEMO"

    @field_validator("icao")
    @classmethod
    def valid_icao(cls, value: str) -> str:
        value = value.upper().strip()
        if len(value) != 4 or not value.isalnum():
            raise ValueError("ICAO debe tener cuatro caracteres alfanuméricos")
        return value

class PavementRating(BaseModel):
    scheme: str = "PCN"
    value: float | None = None
    pavement_type: str | None = None
    subgrade: str | None = None
    tire_pressure_category: str | None = None
    evaluation_method: str | None = None
    raw_value: str | None = None

class Runway(BaseModel):
    designator: str
    length_m: float | None = None
    width_m: float | None = None
    surface: str | None = None
    pavement: PavementRating | None = None
    closed: bool = False
    source_reference: dict[str, Any] | None = None

class Taxiway(BaseModel):
    designator: str
    width_m: float | None = None
    surface: str | None = None
    pavement: PavementRating | None = None
    published_weight_limit_t: float | None = None
    restrictions: list[str] = Field(default_factory=list)
    source_status: str = "DEMO"

class AircraftProfile(BaseModel):
    code: str = "A332F"
    variant: str = "A330-243F"
    manufacturer: str = "Airbus"
    model: str = "A330-200F"
    minimum_runway_length_m: float = 1400
    minimum_runway_width_m: float = 44
    tire_pressure_mpa: float | None = 1.42
    acn_reference_mass_kg: float = 233900
    acn_reference: dict[str, dict[str, float]] = Field(default_factory=lambda: {
        "flexible": {"A": 58, "B": 63, "C": 73, "D": 98},
        "rigid": {"A": 54, "B": 62, "C": 74, "D": 86},
    })
    data_status: str = "REFERENCE_SEED_REQUIRES_CONFIRMATION"

class Notam(BaseModel):
    number: str | None = None
    airport_icao: str
    raw_text: str
    status: str = "ACTIVE"
    decoding_status: str = "DECODED"
    category: str = "OTHER"
    severity: str = "WARNING"
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    source: str = "FAA"
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WeatherObservation(BaseModel):
    station: str
    raw_metar: str
    observed_at: datetime | None = None
    temperature_c: float | None = None
    qnh_hpa: float | None = None
    wind_direction_deg: int | None = None
    wind_speed_kt: float | None = None
    source: str = "AWC"

class WeatherRangeQuery(BaseModel):
    temperature_min_c: float | None = None
    temperature_max_c: float | None = None
    qnh_min_hpa: float | None = None
    qnh_max_hpa: float | None = None
    hours: int = Field(default=24, ge=1, le=168)
    minimum_observations: int = Field(default=1, ge=1)

class ValidationResult(BaseModel):
    rule_code: str
    status: str
    severity: str = "INFO"
    message: str
    actual_value: Any | None = None
    required_value: Any | None = None
    source_reference: dict[str, Any] | None = None

class AssessmentRequest(BaseModel):
    airport_icao: str
    selected_runway: str | None = None
    temperature_min_c: float | None = None
    temperature_max_c: float | None = None
    qnh_min_hpa: float | None = None
    qnh_max_hpa: float | None = None
    aircraft_mass_kg: float = 233900

    @field_validator("airport_icao")
    @classmethod
    def normalize_icao(cls, value: str) -> str:
        value = value.upper().strip()
        if len(value) != 4 or not value.isalnum():
            raise ValueError("ICAO debe tener cuatro caracteres alfanuméricos")
        return value

class Assessment(BaseModel):
    id: str
    airport_icao: str
    status: str
    scope: str = "INFRASTRUCTURE_WEATHER_NOTAM_PRECHECK"
    performance_status: str = "NOT_AVAILABLE"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    validations: list[ValidationResult] = Field(default_factory=list)
    notams: list[Notam] = Field(default_factory=list)
    weather: dict[str, Any] = Field(default_factory=dict)
    snapshots: dict[str, Any] = Field(default_factory=dict)
