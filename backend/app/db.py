from datetime import datetime, timezone
from typing import Any
from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from app.config import settings

class Base(DeclarativeBase):
    pass

class AirportModel(Base):
    __tablename__ = "airports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    icao: Mapped[str] = mapped_column(String(4), unique=True, index=True)
    iata: Mapped[str | None] = mapped_column(String(3), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    elevation_ft: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_status: Mapped[str] = mapped_column(String(32), default="UNKNOWN")
    runways: Mapped[list["RunwayModel"]] = relationship(back_populates="airport", cascade="all, delete-orphan")
    taxiways: Mapped[list["TaxiwayModel"]] = relationship(back_populates="airport", cascade="all, delete-orphan")

class RunwayModel(Base):
    __tablename__ = "runways"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    airport_id: Mapped[int] = mapped_column(ForeignKey("airports.id", ondelete="CASCADE"), index=True)
    designator: Mapped[str] = mapped_column(String(8))
    length_m: Mapped[float | None] = mapped_column(Float)
    width_m: Mapped[float | None] = mapped_column(Float)
    surface: Mapped[str | None] = mapped_column(String(64))
    closed: Mapped[bool] = mapped_column(Boolean, default=False)
    pavement_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    source_reference: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    airport: Mapped[AirportModel] = relationship(back_populates="runways")

class TaxiwayModel(Base):
    __tablename__ = "taxiways"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    airport_id: Mapped[int] = mapped_column(ForeignKey("airports.id", ondelete="CASCADE"), index=True)
    designator: Mapped[str] = mapped_column(String(16))
    width_m: Mapped[float | None] = mapped_column(Float)
    surface: Mapped[str | None] = mapped_column(String(64))
    pavement_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    published_weight_limit_t: Mapped[float | None] = mapped_column(Float)
    restrictions: Mapped[list[str] | None] = mapped_column(JSON)
    airport: Mapped[AirportModel] = relationship(back_populates="taxiways")

class SourceDocumentModel(Base):
    __tablename__ = "source_documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_code: Mapped[str] = mapped_column(String(64), index=True)
    document_type: Mapped[str] = mapped_column(String(64))
    airport_icao: Mapped[str | None] = mapped_column(String(4), index=True)
    revision: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="DISCOVERED", index=True)
    document_url: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str | None] = mapped_column(String(128))
    parser_version: Mapped[str | None] = mapped_column(String(64))
    raw_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class FieldProvenanceModel(Base):
    __tablename__ = "field_provenance"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("source_documents.id", ondelete="CASCADE"), index=True)
    field_path: Mapped[str] = mapped_column(String(255))
    raw_value: Mapped[str | None] = mapped_column(Text)
    normalized_value: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    value_status: Mapped[str] = mapped_column(String(32), default="UNKNOWN")
    confidence: Mapped[float | None] = mapped_column(Float)
    source_reference: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    review_status: Mapped[str] = mapped_column(String(32), default="PENDING")

class AircraftProfileModel(Base):
    __tablename__ = "aircraft_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True)
    variant: Mapped[str] = mapped_column(String(64))
    data_status: Mapped[str] = mapped_column(String(64))
    profile_json: Mapped[dict[str, Any]] = mapped_column(JSON)

class AcnPointModel(Base):
    __tablename__ = "acn_points"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aircraft_profile_id: Mapped[int] = mapped_column(ForeignKey("aircraft_profiles.id", ondelete="CASCADE"), index=True)
    pavement_type: Mapped[str] = mapped_column(String(1))
    subgrade: Mapped[str] = mapped_column(String(1))
    mass_kg: Mapped[float] = mapped_column(Float)
    acn: Mapped[float] = mapped_column(Float)
    source_revision: Mapped[str] = mapped_column(String(128))
    is_official: Mapped[bool] = mapped_column(Boolean, default=False)

class MetarObservationModel(Base):
    __tablename__ = "metar_observations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station: Mapped[str] = mapped_column(String(4), index=True)
    raw_metar: Mapped[str] = mapped_column(Text)
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    temperature_c: Mapped[float | None] = mapped_column(Float)
    qnh_hpa: Mapped[float | None] = mapped_column(Float)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    source: Mapped[str] = mapped_column(String(32), default="AWC")
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class NotamModel(Base):
    __tablename__ = "notams"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    airport_icao: Mapped[str] = mapped_column(String(4), index=True)
    number: Mapped[str | None] = mapped_column(String(64))
    raw_text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE")
    decoding_status: Mapped[str] = mapped_column(String(32), default="UNKNOWN")
    category: Mapped[str] = mapped_column(String(32), default="OTHER")
    severity: Mapped[str] = mapped_column(String(32), default="WARNING")
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class AssessmentModel(Base):
    __tablename__ = "assessments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    airport_icao: Mapped[str] = mapped_column(String(4), index=True)
    status: Mapped[str] = mapped_column(String(64))
    created_by: Mapped[str] = mapped_column(String(128), default="anonymous")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    request_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    result_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)

class ValidationResultModel(Base):
    __tablename__ = "validation_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("assessments.id", ondelete="CASCADE"), index=True)
    rule_code: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32))
    severity: Mapped[str] = mapped_column(String(32))
    message: Mapped[str] = mapped_column(Text)
    actual_value: Mapped[Any | None] = mapped_column(JSON)
    required_value: Mapped[Any | None] = mapped_column(JSON)
    source_reference: Mapped[dict[str, Any] | None] = mapped_column(JSON)

class AuditEventModel(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(128))
    resource_type: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[str | None] = mapped_column(String(128))
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

engine = create_engine(settings.database_url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
