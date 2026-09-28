from collections.abc import Iterable
from app.schemas import WeatherObservation

def evaluate_weather_range(observations: Iterable[WeatherObservation], *, temperature_min_c=None, temperature_max_c=None, qnh_min_hpa=None, qnh_max_hpa=None, minimum_observations=1):
    items = list(observations)
    if len(items) < minimum_observations:
        return {"status": "DATA_INSUFFICIENT", "observations_count": len(items), "message": "No hay suficientes observaciones METAR."}
    temperatures = [x.temperature_c for x in items if x.temperature_c is not None]
    qnhs = [x.qnh_hpa for x in items if x.qnh_hpa is not None]
    temp_min, temp_max = (min(temperatures), max(temperatures)) if temperatures else (None, None)
    qnh_min, qnh_max = (min(qnhs), max(qnhs)) if qnhs else (None, None)
    warnings = []
    if temperature_min_c is not None and temp_min is not None and temp_min < temperature_min_c: warnings.append("La temperatura mínima observada está fuera del rango.")
    if temperature_max_c is not None and temp_max is not None and temp_max > temperature_max_c: warnings.append("La temperatura máxima observada está fuera del rango.")
    if qnh_min_hpa is not None and qnh_min is not None and qnh_min < qnh_min_hpa: warnings.append("El QNH mínimo observado está fuera del rango.")
    if qnh_max_hpa is not None and qnh_max is not None and qnh_max > qnh_max_hpa: warnings.append("El QNH máximo observado está fuera del rango.")
    return {"status": "CONDITIONAL" if warnings else "PASS", "observations_count": len(items), "temperature": {"observed_min_c": temp_min, "observed_max_c": temp_max, "configured_min_c": temperature_min_c, "configured_max_c": temperature_max_c}, "qnh": {"observed_min_hpa": qnh_min, "observed_max_hpa": qnh_max, "configured_min_hpa": qnh_min_hpa, "configured_max_hpa": qnh_max_hpa}, "warnings": warnings}
