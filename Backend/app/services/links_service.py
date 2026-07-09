from app.config import settings
from app.services.db_service import get_user_applications


def get_pages_for_user(username: str, role: str) -> list:
    if not settings.db_enabled:
        raise RuntimeError("La base de datos Oracle no está configurada")
    return get_user_applications(username)
