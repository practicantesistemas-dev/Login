import re
from urllib.parse import urlparse

from app.database import get_connection
from app.queries.user_queries import (
    APPS_BY_USER_QUERY,
    AUTH_USER_QUERY,
    LIST_APPLICATIONS_QUERY,
    LIST_DEPARTMENTS_QUERY,
    USER_BY_USERNAME_QUERY,
    USER_PERMISSIONS_QUERY,
)
from app.schemas.pages import PageLink

_REPORT_TIPO_DEFAULT: str | None = None
FALLBACK_REPORT_USER_TIPO = "user"


def _normalize_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _passwords_match(stored, provided) -> bool:
    stored_norm = _normalize_text(stored)
    provided_norm = _normalize_text(provided)
    if not stored_norm or not provided_norm:
        return False
    if stored_norm == provided_norm:
        return True
    return stored_norm.upper() == provided_norm.upper()


def get_default_report_user_tipo(cursor) -> str:
    """Valor TIPO más frecuente en reportes; fallback si la tabla está vacía."""
    global _REPORT_TIPO_DEFAULT
    if _REPORT_TIPO_DEFAULT:
        return _REPORT_TIPO_DEFAULT

    cursor.execute(
        """
        SELECT TIPO FROM (
            SELECT TIPO, COUNT(*) AS CNT
            FROM BDLIGA.INTRANET_REPORT_USUARIOS
            WHERE TIPO IS NOT NULL AND TRIM(TIPO) IS NOT NULL
            GROUP BY TIPO
            ORDER BY CNT DESC
        )
        WHERE ROWNUM = 1
        """
    )
    row = cursor.fetchone()
    _REPORT_TIPO_DEFAULT = _normalize_text(row[0]) if row and row[0] else FALLBACK_REPORT_USER_TIPO
    return _REPORT_TIPO_DEFAULT


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "aplicacion"


def _extract_host(url: str) -> str:
    normalized = url if "://" in url else f"http://{url}"
    hostname = urlparse(normalized).hostname
    return hostname or url


def _row_to_dict(cursor, row) -> dict:
    columns = [col[0].lower() for col in cursor.description]
    return dict(zip(columns, row))


def _sso_username(data: dict) -> str:
    report_user = _normalize_text(data.get("report_usuario"))
    report_id = _normalize_text(data.get("report_idnum"))
    intranet_user = _normalize_text(data.get("usuario"))
    return report_user or report_id or intranet_user


def _is_active(estado) -> bool:
    value = _normalize_text(estado)
    return value in ("1", "A", "S", "ACTIVO", "TRUE") or value == ""


def _portal_role(data: dict) -> str:
    role = _normalize_text(data.get("portal_rol")).lower()
    if role in ("admin", "area_admin", "usuario"):
        return role
    return "usuario"


def _build_user_dict(data: dict) -> dict:
    usuario = _normalize_text(data.get("usuario"))
    email = _normalize_text(data.get("colemaill")) or _normalize_text(data.get("colemailp"))
    portal_role = _portal_role(data)
    id_area = data.get("id_area")
    return {
        "username": usuario,
        "sso_username": _sso_username(data),
        "nombres": _normalize_text(data.get("nombres")) or usuario,
        "role": portal_role,
        "portal_role": portal_role,
        "id_area": int(id_area) if id_area is not None else None,
        "area_name": _normalize_text(data.get("depdes")),
        "email": email,
        "active": _is_active(data.get("estado")),
    }


def authenticate_user(username: str, password: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(AUTH_USER_QUERY, usuario=username)
            row = cursor.fetchone()
            if not row:
                return None

            data = _row_to_dict(cursor, row)
            if not _is_active(data.get("estado")):
                return None

            report_ok = _passwords_match(data.get("contrasena_report"), password)
            intranet_ok = _passwords_match(data.get("contrasena_intranet"), password)
            if not report_ok and not intranet_ok:
                return None

            return _build_user_dict(data)


def get_sso_credentials(username: str) -> dict | None:
    """Credenciales para abrir apps legacy (reportes o intranet)."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(AUTH_USER_QUERY, usuario=username)
            row = cursor.fetchone()
            if not row:
                return None

            data = _row_to_dict(cursor, row)
            if not _is_active(data.get("estado")):
                return None

            report_pass = _normalize_text(data.get("contrasena_report"))
            intranet_pass = _normalize_text(data.get("contrasena_intranet"))
            password = report_pass or intranet_pass
            if not password:
                return None

            portal_user = _normalize_text(data.get("usuario"))
            app_username = _sso_username(data) or portal_user
            return {
                "password": password,
                "app_username": app_username,
            }


def get_user_by_username(username: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(USER_BY_USERNAME_QUERY, usuario=username)
            row = cursor.fetchone()
            if not row:
                return None

            return _build_user_dict(_row_to_dict(cursor, row))


def _normalize_url_key(url: str) -> str:
    return _normalize_text(url).rstrip("/").lower()


def _normalize_app_key(name: str, url: str) -> str:
    return f"{_normalize_text(name).lower()}|{_normalize_url_key(url)}"


def get_user_applications(username: str) -> list[PageLink]:
    apps: list[PageLink] = []
    seen_ids: set[str] = set()
    seen_apps: set[str] = set()

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(APPS_BY_USER_QUERY, usuario=username)
            for row in cursor:
                data = _row_to_dict(cursor, row)
                name = _normalize_text(data.get("apusno"))
                url = _normalize_text(data.get("apusli"))
                if not name or not url:
                    continue

                app_key = _normalize_app_key(name, url)
                if app_key in seen_apps:
                    continue
                seen_apps.add(app_key)

                base_id = _slugify(name)
                link_id = base_id
                counter = 1
                while link_id in seen_ids:
                    counter += 1
                    link_id = f"{base_id}-{counter}"
                seen_ids.add(link_id)

                apps.append(
                    PageLink(
                        id=link_id,
                        name=name,
                        url=url,
                        ip=_extract_host(url),
                        icon="🔗",
                        description="",
                    )
                )

    return apps


def fetch_user_permission_ids(username: str) -> list[int]:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(USER_PERMISSIONS_QUERY, usuario=username)
            return [int(row[0]) for row in cursor]


def list_departments_from_db() -> list[tuple[int, str]]:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(LIST_DEPARTMENTS_QUERY)
            return [(int(row[0]), _normalize_text(row[1])) for row in cursor if row[1]]


def list_applications_from_db() -> list[tuple[int, str, str]]:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(LIST_APPLICATIONS_QUERY)
            return [
                (int(row[0]), _normalize_text(row[1]), _normalize_text(row[2] or ""))
                for row in cursor
            ]
