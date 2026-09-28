# Reglas SEV v1

## Geometría

- Longitud mínima: `1400 m`.
- Ancho mínimo: `44 m`.
- Estos valores son reglas SEV versionadas, no una afirmación de performance de despegue/aterrizaje.

## Pavimento

- `ACN <= PCN` cuando exista ACN oficial aplicable.
- Validar categoría de presión de neumáticos.
- PCN no equivale a toneladas.
- Si existe peso máximo explícito publicado, conservarlo como dato de fuente.
- Si faltan datos oficiales, devolver advertencia/indeterminado.
- No aprobar automáticamente sobrecarga.

## NOTAM

- Pista cerrada o restricción bloqueante: bloqueo si afecta la pista/ruta evaluada.
- NOTAM no descodificable: warning, conservando el texto literal.

## METAR

- Consultas bajo demanda.
- Temperatura y QNH fuera de rango: warning/conditional.
- Sin observaciones suficientes: `DATA_INSUFFICIENT`.

## Estados

`VIABLE_FROM_INFRASTRUCTURE`, `CONDITIONAL`, `NOT_VIABLE_FROM_INFRASTRUCTURE`, `BLOCKED_BY_NOTAM`, `DATA_INSUFFICIENT`, `REQUIRES_REVIEW`.
