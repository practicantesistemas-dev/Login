from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import oracledb

from app.core.security import decode_access_token
from app.services.users_service import get_user_by_username

security = HTTPBearer()
ADMIN_ROLES = {"admin", "area_admin"}


def _db_unavailable_detail(exc: Exception) -> str:
    message = str(exc)
    if "ORA-12170" in message or "TNS" in message.upper():
        return "No se pudo conectar con Oracle (tiempo de espera agotado). Verifique red/VPN e intente de nuevo."
    if isinstance(exc, RuntimeError):
        return str(exc)
    return "No se pudo conectar con la base de datos. Intente de nuevo en unos segundos."


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    try:
        user = get_user_by_username(username)
    except (oracledb.Error, RuntimeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_db_unavailable_detail(exc),
        ) from exc

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    if user.get("active") is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo",
        )

    return user


async def require_admin_access(
    current_user: dict = Depends(get_current_user),
) -> dict:
    role = current_user.get("portal_role") or current_user.get("role")
    if role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administración",
        )
    return current_user
