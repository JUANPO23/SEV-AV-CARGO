# Arquitectura SEV v1

SEV v1 es un monolito modular con límites claros para evolucionar a servicios independientes cuando el volumen o la operación lo requieran.

```text
React/Vite -> FastAPI -> domain/application services -> PostgreSQL
                         |-> FAA NOTAM (on-demand)
                         |-> AWC METAR (on-demand)
                         |-> AIP connectors/manual review
                         |-> Redis short cache (optional)
```

## Límites

- `schemas.py`: contrato canónico y validación de entrada.
- `pavement.py`: PCN, presión y ACN-PCN, sin conversiones ficticias a toneladas.
- `demo.py`: almacenamiento temporal/fixture de desarrollo; debe reemplazarse por repositorios SQLAlchemy en la siguiente iteración.
- `api/routes.py`: transporte HTTP y proveedores on-demand.

La versión inicial contiene una base ejecutable y demostrable. La persistencia productiva, autenticación y conectores oficiales específicos de cada AIP deben entrar antes de usar el sistema en operación real.
