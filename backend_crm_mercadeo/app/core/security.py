"""Valida tokens JWT emitidos por el backend Login/SSO, usando el mismo
SECRET_KEY/ALGORITHM, para identificar al usuario del portal detras de un
endpoint protegido de este backend (ej. quien registra un seguimiento)."""

from jose import JWTError, jwt

from app.core.config import settings


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
