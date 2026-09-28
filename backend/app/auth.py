from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.config import settings

bearer = HTTPBearer(auto_error=False)

def current_actor(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    if not settings.auth_enabled:
        return "development-user"
    if not credentials or credentials.credentials != settings.dev_api_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credencial inválida")
    return "authenticated-user"
