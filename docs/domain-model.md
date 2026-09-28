# Modelo de dominio

Entidades previstas:

- `Airport`: identificación OACI, IATA, nombre, ubicación y fuente.
- `Runway`: geometría, superficie, cierre, distancias declaradas y pavimento.
- `Taxiway`: designador, ancho, superficie, PCN/PCR, peso explícito y restricciones.
- `SourceDocument`/`AipRevision`: documento original, ciclo, hash, parser, vigencia y estado.
- `FieldProvenance`: fuente por campo, página/sección, texto original, confianza y revisión.
- `AircraftProfile`: A330-243F, reglas geométricas y referencia ACN versionada.
- `MetarObservation` y `Notam`: payload original y normalización.
- `Assessment`: snapshot reproducible con validaciones y estado final.

Un valor ausente no se transforma en cero. Debe conservarse su estado: `PRESENT`, `NOT_PUBLISHED`, `NOT_APPLICABLE`, `UNKNOWN`, `PARSE_ERROR` o `CONFLICTING`.
