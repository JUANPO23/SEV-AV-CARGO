# SEV-AV-CARGO

Sistema de pre-evaluación de infraestructura aeroportuaria, METAR y NOTAM para operaciones con Airbus A330-243F.

> **Alcance v1:** SEV no ejecuta Airbus PEP ni realiza cálculos de performance de despegue o aterrizaje. El resultado es una pre-evaluación que requiere validación operacional.

## Stack

- Backend: Python 3.12, FastAPI, Pydantic v2
- Persistencia preparada: SQLAlchemy/Alembic + PostgreSQL
- Caché opcional: Redis para consultas on-demand de corta duración
- Proveedores: FAA NOTAM y Aviation Weather Center METAR
- Frontend: React + TypeScript + Vite

## Inicio rápido

```bash
docker compose up --build
```

API: `http://localhost:8000`
Documentación OpenAPI: `http://localhost:8000/docs`
Frontend: `http://localhost:5173`

Para ejecutar el backend localmente:

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

## Configuración

Copiar `.env.example` a `.env`. El modo demo permite ejecutar la API sin credenciales ni acceso de red a proveedores externos.

## Ejemplos

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/airports/SKUC
curl http://localhost:8000/api/v1/airports/SKUC/notams/live
curl 'http://localhost:8000/api/v1/airports/SKUC/weather/range?hours=24&temperature_min_c=18&temperature_max_c=35&qnh_min_hpa=1000&qnh_max_hpa=1025'
```

## Limitaciones importantes

- La consulta de NOTAM y METAR es únicamente bajo demanda; no hay recolectores en segundo plano.
- Las AIP son heterogéneas por país. La v1 conserva documentos y ofrece un registro manual seguro; los conectores específicos se incorporan por fuente.
- PCN no se convierte directamente a toneladas. Se usa peso explícito publicado cuando existe; ACN-PCN solo se evalúa con datos oficiales aplicables.
- Un NOTAM no descodificable se conserva y genera advertencia, no bloqueo automático.
- La v1 no autoriza operaciones ni sustituye despacho, performance, autoridad aeroportuaria o tripulación.

## Documentación

- [Arquitectura](docs/architecture.md)
- [Modelo de dominio](docs/domain-model.md)
- [Reglas](docs/rules.md)
- [Fuentes y limitaciones](docs/data-sources.md)
