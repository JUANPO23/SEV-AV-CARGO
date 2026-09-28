# Fuentes y límites

- AIP: fuentes heterogéneas por país. SEV debe usar conectores específicos, preservando el documento original y la procedencia de cada campo. La v1 ofrece registro manual y fixture; no afirma cobertura mundial.
- NOTAM: FAA, bajo demanda y configurable. La cobertura para aeropuertos fuera de la red disponible debe informarse; no se debe inferir que ausencia de resultados equivale a ausencia universal de NOTAM.
- METAR: Aviation Weather Center, bajo demanda. Si no entrega histórico suficiente, SEV no inventa una serie temporal y devuelve datos insuficientes.
- Aeronave: Airbus A330-243F. Los valores ACN de referencia incluidos en el fixture están marcados como `REFERENCE_SEED_REQUIRES_CONFIRMATION`; deben validarse contra la revisión oficial de Airbus antes de uso operacional.
- PEP: fuera de v1.
