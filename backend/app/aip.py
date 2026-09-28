from typing import Any
from app.schemas import PavementRating

class AipConnector:
    source_code = "GENERIC_MANUAL"
    def extract(self, document: dict[str, Any]) -> dict[str, Any]:
        return {"status": "REVIEW_REQUIRED", "source_code": self.source_code, "data": document.get("data", {}), "warnings": ["Conector genérico: requiere revisión humana."]}

class ColombiaAisConnector(AipConnector):
    source_code = "CO_AIS"

class FaaNasrConnector(AipConnector):
    source_code = "US_FAA_NASR"

CONNECTORS = {x.source_code: x for x in [AipConnector(), ColombiaAisConnector(), FaaNasrConnector()]}

def get_connector(source_code: str) -> AipConnector:
    return CONNECTORS.get(source_code, CONNECTORS["GENERIC_MANUAL"])
