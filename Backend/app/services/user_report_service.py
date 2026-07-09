from app.database import get_connection
from app.queries.user_queries import (
    LIST_USERS_SUMMARY_QUERY,
    LIST_USERS_WITH_APPS_QUERY,
)


def _normalize_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _row_to_dict(cursor, row) -> dict:
    columns = [col[0].lower() for col in cursor.description]
    return dict(zip(columns, row))


def _is_active(estado) -> bool:
    return _normalize_text(estado) in ("1", "A", "S", "ACTIVO", "TRUE")


def _area_filter(actor: dict) -> tuple[str, dict]:
    if actor.get("portal_role") == "area_admin":
        return "AND t0.ID_AREA = :id_area", {"id_area": actor.get("id_area")}
    return "", {}


def list_users_summary(actor: dict) -> list[dict]:
    """Una fila por usuario con conteo de apps."""
    area_filter, params = _area_filter(actor)
    query = LIST_USERS_SUMMARY_QUERY.format(area_filter=area_filter)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, **params)
            rows = []
            for row in cursor:
                data = _row_to_dict(cursor, row)
                rows.append(
                    {
                        "id_usuario": data.get("id_usuario"),
                        "username": _normalize_text(data.get("usuario")),
                        "nombres": _normalize_text(data.get("nombres")),
                        "num_id": _normalize_text(data.get("num_id")),
                        "id_area": data.get("id_area"),
                        "departamento": _normalize_text(data.get("depdes")),
                        "portal_role": _normalize_text(data.get("portal_rol")) or "usuario",
                        "active": _is_active(data.get("estado")),
                        "email_laboral": _normalize_text(data.get("colemaill")),
                        "email_personal": _normalize_text(data.get("colemailp")),
                        "report_usuario": _normalize_text(data.get("report_usuario")),
                        "report_idnum": _normalize_text(data.get("report_idnum")),
                        "area_report": _normalize_text(data.get("area_report")),
                        "total_apps": int(data.get("total_apps") or 0),
                    }
                )
            return rows


def list_users_with_apps(actor: dict, username: str | None = None) -> list[dict]:
    """Usuarios con detalle de cada app (puede repetir filas por usuario)."""
    area_filter, params = _area_filter(actor)
    user_filter = ""
    if username:
        user_filter = "AND UPPER(TRIM(t0.USUARIO)) = UPPER(TRIM(:usuario))"
        params["usuario"] = username.strip()

    query = LIST_USERS_WITH_APPS_QUERY.format(
        area_filter=area_filter,
        user_filter=user_filter,
    )

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, **params)
            return [_row_to_dict(cursor, row) for row in cursor]


def list_users_grouped(actor: dict, username: str | None = None) -> list[dict]:
    """Usuarios agrupados con lista de aplicaciones anidadas."""
    flat_rows = list_users_with_apps(actor, username)
    grouped: dict[str, dict] = {}

    for row in flat_rows:
        user_key = _normalize_text(row.get("usuario")).lower()
        if not user_key:
            continue

        if user_key not in grouped:
            grouped[user_key] = {
                "id_usuario": row.get("id_usuario"),
                "username": _normalize_text(row.get("usuario")),
                "nombres": _normalize_text(row.get("nombres")),
                "num_id": _normalize_text(row.get("num_id")),
                "id_area": row.get("id_area"),
                "departamento": _normalize_text(row.get("depdes")),
                "portal_role": _normalize_text(row.get("portal_rol")) or "usuario",
                "active": _is_active(row.get("estado")),
                "email_laboral": _normalize_text(row.get("colemaill")),
                "email_personal": _normalize_text(row.get("colemailp")),
                "report_usuario": _normalize_text(row.get("report_usuario")),
                "report_idnum": _normalize_text(row.get("report_idnum")),
                "applications": [],
            }

        app_id = row.get("apusid")
        app_name = _normalize_text(row.get("apusno"))
        if app_id is not None and app_name:
            grouped[user_key]["applications"].append(
                {
                    "id": int(app_id),
                    "name": app_name,
                    "url": _normalize_text(row.get("apusli")),
                }
            )

    return sorted(grouped.values(), key=lambda item: (item["nombres"], item["username"]))
