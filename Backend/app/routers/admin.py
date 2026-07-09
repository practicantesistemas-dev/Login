from fastapi import APIRouter, Depends, HTTPException, status
import oracledb

from app.dependencies import require_admin_access
from app.schemas.admin import (
    ApplicationEstadoRequest,
    ApplicationEstadoResponse,
    ApplicationItem,
    DepartmentItem,
    ManagedUser,
    UserCreateRequest,
    UserUpdateRequest,
)
from app.services import admin_service
from app.services import user_report_service

router = APIRouter(prefix="/admin", tags=["admin"])


def _oracle_error_detail(exc: oracledb.Error) -> str:
    message = str(exc)
    if "ORA-01400" in message:
        return "Faltan datos obligatorios en la base de datos. Verifique cédula, área y contraseña."
    if "ORA-00001" in message:
        return "Ya existe un registro duplicado para ese usuario o cédula."
    return "No se pudo completar la operación en la base de datos."


@router.get("/departments", response_model=list[DepartmentItem])
async def get_departments(_: dict = Depends(require_admin_access)):
    return admin_service.list_departments()


@router.get("/applications", response_model=list[ApplicationItem])
async def get_applications(
    estado: str | None = None,
    _: dict = Depends(require_admin_access),
):
    if estado and estado not in ("activa", "inactiva"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El filtro estado debe ser 'activa' o 'inactiva'",
        )
    return admin_service.list_applications(estado=estado)


@router.patch("/applications/estado", response_model=ApplicationEstadoResponse)
async def set_application_estado(
    payload: ApplicationEstadoRequest,
    _: dict = Depends(require_admin_access),
):
    try:
        return admin_service.set_application_estado_by_url(payload.url, payload.estado)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL no encontrada en el catálogo")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/users/full")
async def get_users_full(current_user: dict = Depends(require_admin_access)):
    """Usuarios completos con apps anidadas (query Oracle en Python)."""
    return user_report_service.list_users_grouped(current_user)


@router.get("/users/full/{username}")
async def get_user_full(username: str, current_user: dict = Depends(require_admin_access)):
    users = user_report_service.list_users_grouped(current_user, username)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return users[0]


@router.get("/users/summary")
async def get_users_summary(current_user: dict = Depends(require_admin_access)):
    """Resumen: una fila por usuario + total de apps."""
    return user_report_service.list_users_summary(current_user)


@router.get("/users", response_model=list[ManagedUser])
async def get_users(
    id_area: int | None = None,
    q: str | None = None,
    current_user: dict = Depends(require_admin_access),
):
    return admin_service.list_managed_users(current_user, department_id=id_area, search=q)


@router.get("/users/{username}", response_model=ManagedUser)
async def get_user(username: str, current_user: dict = Depends(require_admin_access)):
    user = admin_service.get_managed_user(current_user, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@router.post("/users", response_model=ManagedUser, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreateRequest, current_user: dict = Depends(require_admin_access)):
    try:
        return admin_service.create_managed_user(current_user, payload)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except oracledb.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_oracle_error_detail(exc),
        )
    except oracledb.Error as exc:
        message = str(exc)
        if "ORA-12170" in message or "TNS" in message.upper():
            detail = "No se pudo conectar con Oracle (tiempo de espera agotado). Verifique red/VPN e intente de nuevo."
        else:
            detail = "Error de base de datos. Intente de nuevo en unos segundos."
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


@router.put("/users/{username}", response_model=ManagedUser)
async def update_user(
    username: str,
    payload: UserUpdateRequest,
    current_user: dict = Depends(require_admin_access),
):
    try:
        return admin_service.update_managed_user(current_user, username, payload)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except oracledb.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_oracle_error_detail(exc),
        )
    except oracledb.Error as exc:
        message = str(exc)
        if "ORA-12170" in message or "TNS" in message.upper():
            detail = "No se pudo conectar con Oracle (tiempo de espera agotado). Verifique red/VPN e intente de nuevo."
        else:
            detail = "Error de base de datos. Intente de nuevo en unos segundos."
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


@router.post("/users/{username}/deactivate", response_model=ManagedUser)
async def deactivate_user(username: str, current_user: dict = Depends(require_admin_access)):
    try:
        return admin_service.deactivate_managed_user(current_user, username)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
