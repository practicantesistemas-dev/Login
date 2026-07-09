from app.config import settings
from app.services.db_service import authenticate_user as db_authenticate
from app.services.db_service import get_user_by_username as db_get_user


def authenticate_user(username: str, password: str) -> dict | None:
    if not settings.db_enabled:
        raise RuntimeError("La base de datos Oracle no está configurada")
    return db_authenticate(username, password)


def get_user_by_username(username: str) -> dict | None:
    if not settings.db_enabled:
        raise RuntimeError("La base de datos Oracle no está configurada")
    return db_get_user(username)
