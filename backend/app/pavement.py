import re
from .schemas import PavementRating

PCN_RE = re.compile(r"(?:PCN\s*)?(?P<value>\d+(?:\.\d+)?)\s*/\s*(?P<pavement>[FR])\s*/\s*(?P<subgrade>[ABCD])\s*/\s*(?P<pressure>[WXYZ])\s*/\s*(?P<method>[TU])", re.I)

def parse_pcn(value: str) -> PavementRating | None:
    match = PCN_RE.search(value.strip())
    if not match:
        return None
    data = match.groupdict()
    return PavementRating(
        scheme="PCN",
        value=float(data["value"]),
        pavement_type=data["pavement"].upper(),
        subgrade=data["subgrade"].upper(),
        tire_pressure_category=data["pressure"].upper(),
        evaluation_method=data["method"].upper(),
        raw_value=value,
    )

def pressure_limit_mpa(category: str | None) -> float | None:
    return {"W": None, "X": 1.75, "Y": 1.25, "Z": 0.50}.get((category or "").upper())

def reference_acn(aircraft, pavement: PavementRating) -> float | None:
    if pavement.scheme != "PCN" or not pavement.pavement_type or not pavement.subgrade:
        return None
    kind = "flexible" if pavement.pavement_type.upper() == "F" else "rigid" if pavement.pavement_type.upper() == "R" else None
    if not kind:
        return None
    return aircraft.acn_reference.get(kind, {}).get(pavement.subgrade.upper())

def evaluate_pcn(aircraft, pavement: PavementRating, mass_kg: float) -> dict:
    acn = reference_acn(aircraft, pavement)
    if acn is None:
        return {"status": "WARNING", "severity": "WARNING", "acn": None, "message": "No existe un ACN oficial aplicable para este pavimento; no se determina compatibilidad."}
    limit = pressure_limit_mpa(pavement.tire_pressure_category)
    pressure_ok = limit is None or (aircraft.tire_pressure_mpa is not None and aircraft.tire_pressure_mpa <= limit)
    if not pressure_ok:
        return {"status": "BLOCKING", "severity": "BLOCKING", "acn": acn, "message": "La presión de neumáticos supera el límite publicado del pavimento."}
    compatible = acn <= (pavement.value or 0)
    return {
        "status": "PASS" if compatible else "FAIL",
        "severity": "INFO" if compatible else "BLOCKING",
        "acn": acn,
        "pcn": pavement.value,
        "mass_kg": mass_kg,
        "message": "ACN <= PCN; pavimento compatible." if compatible else "ACN > PCN; se requiere revisión/autorización de la autoridad.",
    }
