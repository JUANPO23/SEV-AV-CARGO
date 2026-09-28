from datetime import datetime, timezone
from typing import Any
import json
import re
import httpx
from app.config import settings
from app.schemas import Notam, WeatherObservation

class ProviderError(RuntimeError):
    pass

class ShortCache:
    def __init__(self):
        self._items: dict[str, tuple[datetime, Any]] = {}
    def get(self, key: str):
        item = self._items.get(key)
        if not item or (datetime.now(timezone.utc) - item[0]).total_seconds() > 300:
            return None
        return item[1]
    def set(self, key: str, value: Any):
        self._items[key] = (datetime.now(timezone.utc), value)

cache = ShortCache()

class FaaNotamClient:
    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self.http_client = http_client
    async def search(self, icao: str) -> list[Notam]:
        key = f"notam:{icao.upper()}"
        cached = cache.get(key)
        if cached is not None:
            return cached
        if settings.demo_mode:
            return []
        if not settings.faa_notam_api_key:
            raise ProviderError("FAA_NOTAM_API_KEY no configurada")
        client = self.http_client or httpx.AsyncClient(timeout=settings.request_timeout_seconds)
        close = self.http_client is None
        try:
            response = await client.get(f"{settings.faa_notam_base_url}/notams", params={"icaoLocation": icao.upper()}, headers={"X-API-KEY": settings.faa_notam_api_key, "Accept": "application/json"})
            response.raise_for_status()
            payload = response.json()
            raw_items = payload if isinstance(payload, list) else payload.get("notams", payload.get("items", []))
            result = [self._normalize(icao, item) for item in raw_items]
            cache.set(key, result)
            return result
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            raise ProviderError(f"Error consultando FAA NOTAM: {exc}") from exc
        finally:
            if close:
                await client.aclose()
    def _normalize(self, icao: str, item: dict[str, Any]) -> Notam:
        raw = str(item.get("text") or item.get("notamText") or item.get("rawText") or item)
        decoded = bool(item.get("decoded") or item.get("notamNumber") or item.get("notamNumber"))
        category = "OTHER"
        upper = raw.upper()
        for token, value in (("RWY", "RUNWAY"), ("TWY", "TAXIWAY"), ("APRON", "APRON"), ("NAV", "NAVIGATION_AID")):
            if token in upper:
                category = value; break
        severity = "WARNING"
        if "CLSD" in upper or "CLOSED" in upper:
            severity = "BLOCKING"
        return Notam(airport_icao=icao.upper(), number=item.get("notamNumber") or item.get("number"), raw_text=raw, decoding_status="DECODED" if decoded else "FAILED", category=category, severity=severity, source="FAA")

class AwcMetarClient:
    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self.http_client = http_client
    async def search(self, icao: str, hours: int = 24) -> list[WeatherObservation]:
        key = f"metar:{icao.upper()}:{hours}"
        cached = cache.get(key)
        if cached is not None:
            return cached
        if settings.demo_mode:
            return []
        client = self.http_client or httpx.AsyncClient(timeout=settings.request_timeout_seconds, headers={"User-Agent": "SEV-AV-CARGO/1.0"})
        close = self.http_client is None
        try:
            response = await client.get(f"{settings.awc_base_url}/metar", params={"ids": icao.upper(), "format": "json", "hours": hours})
            if response.status_code == 204:
                return []
            response.raise_for_status()
            payload = response.json()
            result = [self._normalize(item) for item in (payload if isinstance(payload, list) else payload.get("data", []))]
            cache.set(key, result)
            return result
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderError(f"Error consultando AWC METAR: {exc}") from exc
        finally:
            if close:
                await client.aclose()
    def _normalize(self, item: dict[str, Any]) -> WeatherObservation:
        temp = item.get("temp")
        qnh = item.get("altim") or item.get("altimeter")
        if isinstance(qnh, str):
            qnh = float(qnh.replace("Q", "")) if qnh.replace("Q", "").replace(".", "", 1).isdigit() else None
        return WeatherObservation(station=item.get("icaoId") or item.get("station", ""), raw_metar=item.get("rawOb", json.dumps(item)), observed_at=datetime.fromisoformat(item["reportTime"].replace("Z", "+00:00")) if item.get("reportTime") else None, temperature_c=temp, qnh_hpa=qnh, wind_direction_deg=item.get("wdir"), wind_speed_kt=item.get("wspd"), source="AWC")
