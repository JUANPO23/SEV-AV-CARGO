# SEV v1.1 - persistencia, proveedores y auditoría

Esta iteración incorpora:

- modelos SQLAlchemy y creación/migración Alembic;
- persistencia de evaluaciones y resultados;
- snapshots reproducibles y auditoría;
- cliente FAA NOTAM bajo demanda con API key configurable;
- cliente Aviation Weather Center METAR bajo demanda;
- caché corta en memoria (5 minutos), sustituible por Redis sin cambiar el dominio;
- registro y revisión manual de documentos AIP;
- conectores AIP genérico/manual, Colombia AIS y FAA NASR como puntos de extensión;
- modelo versionado para perfiles ACN y puntos de referencia;
- autenticación Bearer opcional para entornos internos;
- frontend de investigación y evaluación.

## Migraciones

```bash
cd backend
pip install -e '.[dev]'
alembic -c alembic.ini upgrade head
uvicorn app.main:app --reload
```

En desarrollo, la API crea tablas automáticamente cuando `APP_ENV=development`. Para producción usar Alembic y PostgreSQL:

```bash
DATABASE_URL=postgresql+psycopg://sev:sev@localhost:5432/sev alembic upgrade head
```

## Proveedores

Con `DEMO_MODE=true`, no se hacen llamadas externas. Para activar consultas reales configure `DEMO_MODE=false`, `FAA_NOTAM_API_KEY` y `AWC_BASE_URL`. La API de METAR de AWC permite consultar por ICAO y conserva hasta 30 días de datos, pero las solicitudes deben limitarse y respetar rate limits. FAA NOTAM requiere API key para el servicio REST; si falla la configuración, SEV devuelve error explícito y no inventa resultados.

## Auth

`AUTH_ENABLED=false` es útil para desarrollo. En un entorno interno active `AUTH_ENABLED=true` y envíe:

```text
Authorization: Bearer <DEV_API_TOKEN>
```

El token de desarrollo debe reemplazarse por un proveedor corporativo OIDC/Entra ID antes de producción.
