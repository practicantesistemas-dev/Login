from app.database import get_connection
from app.queries.user_queries import LIST_APPLICATIONS_QUERY, LIST_DEPARTMENTS_QUERY
from app.schemas.admin import (
    ApplicationEstadoResponse,
    ApplicationItem,
    DepartmentItem,
    ManagedUser,
    UserCreateRequest,
    UserUpdateRequest,
)
from app.services.db_service import fetch_user_permission_ids

PORTAL_ROLES = {"admin", "area_admin", "usuario"}
REPORT_PASSWORD_MAX = 20
INTRANET_PASSWORD_MAX = 40
REPORT_TIPO_FALLBACK = "user"
REPORT_TIPOS_KNOWN = frozenset({"user", "root"})


def _validate_password(password: str, *, required: bool = True) -> str:
    value = _normalize_text(password)
    if not value:
        if required:
            raise ValueError("La contraseña es obligatoria")
        return ""
    if len(value) > REPORT_PASSWORD_MAX:
        raise ValueError(
            f"La contraseña no puede superar {REPORT_PASSWORD_MAX} caracteres "
            "(límite de INTRANET_REPORT_USUARIOS)"
        )
    return value


def _validate_report_tipo(report_tipo: str, allowed: set[str] | None = None) -> str:
    value = _normalize_text(report_tipo).lower()
    if not value:
        raise ValueError("El tipo de usuario en reportes es obligatorio")
    if len(value) > 10:
        raise ValueError("El tipo de usuario en reportes no puede superar 10 caracteres")
    if allowed and value not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise ValueError(f"Tipo de reportes inválido. Valores permitidos: {allowed_text}")
    return value


def list_report_user_tipos() -> list[str]:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT TIPO
                FROM BDLIGA.INTRANET_REPORT_USUARIOS
                WHERE TIPO IS NOT NULL AND TRIM(TIPO) IS NOT NULL
                GROUP BY TIPO
                ORDER BY COUNT(*) DESC, TIPO
                """
            )
            tipos = [_normalize_text(row[0]).lower() for row in cursor if row[0]]
    if not tipos:
        return [REPORT_TIPO_FALLBACK]
    return tipos


def _normalize_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _row_to_dict(cursor, row) -> dict:
    columns = [col[0].lower() for col in cursor.description]
    return dict(zip(columns, row))


def _is_active(estado) -> bool:
    return _normalize_text(estado) in ("1", "A", "S", "ACTIVO", "TRUE")


def _next_id(cursor, table: str, column: str = "ID") -> int:
    cursor.execute(f"SELECT NVL(MAX({column}), 0) + 1 FROM BDLIGA.{table}")
    return int(cursor.fetchone()[0])


def _can_manage_target(actor: dict, target_role: str, target_area: int | None) -> None:
    actor_role = actor.get("portal_role", "usuario")
    if actor_role == "admin":
        return
    if actor_role != "area_admin":
        raise PermissionError("No autorizado")

    if target_role in ("admin", "area_admin"):
        raise PermissionError("Solo el administrador global puede asignar ese rol")

    actor_area = actor.get("id_area")
    if actor_area is None or target_area != actor_area:
        raise PermissionError("Solo puede gestionar usuarios de su departamento")


def list_departments() -> list[DepartmentItem]:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(LIST_DEPARTMENTS_QUERY)
            return [
                DepartmentItem(id=int(row[0]), name=_normalize_text(row[1]))
                for row in cursor
                if row[1]
            ]


def _normalize_app_estado(value) -> str:
    estado = _normalize_text(value).lower()
    return "activa" if estado == "activa" else "inactiva"


def _normalize_url_key(url: str) -> str:
    return _normalize_text(url).rstrip("/").lower()


def _normalize_app_key(name: str, url: str) -> str:
    return f"{_normalize_text(name).lower()}|{_normalize_url_key(url)}"


def list_applications(estado: str | None = None) -> list[ApplicationItem]:
    params: dict = {}
    estado_filter = ""
    if estado in ("activa", "inactiva"):
        estado_filter = "AND NVL(PORTAL_ESTADO, 'inactiva') = :estado"
        params["estado"] = estado

    query = f"""
        SELECT
            a.APUSID,
            a.APUSNO,
            a.APUSLI,
            NVL(a.PORTAL_ESTADO, 'inactiva') AS PORTAL_ESTADO,
            (
                SELECT COUNT(*)
                FROM BDLIGA.INTRANET_APLICACIONES_USUARIOS x
                WHERE x.APUSLI IS NOT NULL
                  AND LOWER(RTRIM(TRIM(x.APUSLI), '/')) = LOWER(RTRIM(TRIM(a.APUSLI), '/'))
            ) AS LINK_COUNT
        FROM BDLIGA.INTRANET_APLICACIONES_USUARIOS a
        WHERE a.APUSNO IS NOT NULL
          AND a.APUSLI IS NOT NULL
        {estado_filter}
        ORDER BY a.APUSNO, a.APUSID
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, **params)
            items: list[ApplicationItem] = []
            seen_apps: set[str] = set()
            for row in cursor:
                name = _normalize_text(row[1])
                url = _normalize_text(row[2])
                if not name or not url:
                    continue
                app_key = _normalize_app_key(name, url)
                if app_key in seen_apps:
                    continue
                seen_apps.add(app_key)
                items.append(
                    ApplicationItem(
                        id=int(row[0]),
                        name=name,
                        url=url,
                        estado=_normalize_app_estado(row[3]),
                        linked_count=int(row[4] or 1),
                    )
                )
            return items


def set_application_estado_by_url(url: str, estado: str) -> ApplicationEstadoResponse:
    normalized_estado = _normalize_app_estado(estado)
    url_key = _normalize_url_key(url)
    if not url_key:
        raise ValueError("La URL es obligatoria")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE BDLIGA.INTRANET_APLICACIONES_USUARIOS
                SET PORTAL_ESTADO = :estado
                WHERE APUSLI IS NOT NULL
                  AND LOWER(RTRIM(TRIM(APUSLI), '/')) = :url_key
                """,
                estado=normalized_estado,
                url_key=url_key,
            )
            updated = cursor.rowcount
            if updated == 0:
                raise LookupError("URL no encontrada")

            cursor.execute(
                """
                SELECT APUSNO, APUSLI, NVL(PORTAL_ESTADO, 'inactiva')
                FROM BDLIGA.INTRANET_APLICACIONES_USUARIOS
                WHERE APUSLI IS NOT NULL
                  AND LOWER(RTRIM(TRIM(APUSLI), '/')) = :url_key
                ORDER BY APUSID
                FETCH FIRST 1 ROW ONLY
                """,
                url_key=url_key,
            )
            row = cursor.fetchone()
            conn.commit()

    name = _normalize_text(row[0]) if row else ""
    final_url = _normalize_text(row[1]) if row else url.strip()
    return ApplicationEstadoResponse(
        url=final_url,
        name=name,
        estado=_normalize_app_estado(row[2]) if row else normalized_estado,
        updated_count=int(updated),
    )


def _build_managed_user(data: dict, app_ids: list[int]) -> ManagedUser:
    portal_role = _normalize_text(data.get("portal_rol")) or "usuario"
    if portal_role not in PORTAL_ROLES:
        portal_role = "usuario"

    id_area = data.get("id_area")
    id_usuario = data.get("id_usuario")
    return ManagedUser(
        id_usuario=int(id_usuario) if id_usuario is not None else None,
        username=_normalize_text(data.get("usuario")),
        nombres=_normalize_text(data.get("nombres")),
        num_id=_normalize_text(data.get("num_id")),
        id_area=int(id_area) if id_area is not None else None,
        area_name=_normalize_text(data.get("depdes")),
        email_personal=_normalize_text(data.get("colemailp")),
        email_laboral=_normalize_text(data.get("colemaill")),
        portal_role=portal_role,
        report_tipo=_normalize_text(data.get("report_tipo")).lower() or REPORT_TIPO_FALLBACK,
        active=_is_active(data.get("estado")),
        app_ids=app_ids,
    )


def _managed_users_base_query(extra_filters: str) -> str:
    """Una fila por usuario; emails vía subconsulta (evita duplicados por JOIN colaboradores)."""
    return f"""
        SELECT
            u.ID                                        AS ID_USUARIO,
            u.USUARIO                                   AS USUARIO,
            u.NOMBRES                                   AS NOMBRES,
            u.NUM_ID                                    AS NUM_ID,
            u.ID_AREA                                   AS ID_AREA,
            u.PORTAL_ROL                                AS PORTAL_ROL,
            u.ESTADO                                    AS ESTADO,
            d.DEPDES                                    AS DEPDES,
            (
                SELECT MAX(c.COLEMAILP)
                FROM BDLIGA.INTRANET_COLABORADORES c
                WHERE c.COLNID = TO_CHAR(u.NUM_ID)
            )                                           AS COLEMAILP,
            (
                SELECT MAX(c.COLEMAILL)
                FROM BDLIGA.INTRANET_COLABORADORES c
                WHERE c.COLNID = TO_CHAR(u.NUM_ID)
            )                                           AS COLEMAILL,
            (
                SELECT MAX(r.TIPO)
                FROM BDLIGA.INTRANET_REPORT_USUARIOS r
                WHERE r.IDNUM = TO_CHAR(u.NUM_ID)
            )                                           AS REPORT_TIPO
        FROM BDLIGA.INTRANET_USUARIOS u
        LEFT JOIN BDLIGA.INTRANET_DEPARTAMENTOS d ON u.ID_AREA = d.DEPID
        WHERE 1 = 1
        {extra_filters}
        ORDER BY u.NOMBRES, u.USUARIO
    """


def _fetch_permissions_map(cursor) -> dict[str, list[int]]:
    """Carga todos los permisos en una sola consulta."""
    cursor.execute(
        """
        SELECT PERMUSU, PERMAPP
        FROM BDLIGA.INTRANET_APP_PERMISOS
        ORDER BY PERMUSU, PERMAPP
        """
    )
    permissions: dict[str, list[int]] = {}
    for permusu, permapp in cursor:
        if permapp is None:
            continue
        key = _normalize_text(permusu).upper()
        permissions.setdefault(key, []).append(int(permapp))
    return permissions


def list_managed_users(
    actor: dict,
    department_id: int | None = None,
    search: str | None = None,
) -> list[ManagedUser]:
    params: dict = {}
    filters: list[str] = []

    if actor.get("portal_role") == "area_admin":
        filters.append("AND u.ID_AREA = :actor_area")
        params["actor_area"] = actor.get("id_area")
    elif department_id is not None:
        filters.append("AND u.ID_AREA = :department_id")
        params["department_id"] = department_id

    search_term = _normalize_text(search)
    if search_term:
        filters.append(
            "AND (UPPER(u.NOMBRES) LIKE :search OR UPPER(u.USUARIO) LIKE :search)"
        )
        params["search"] = f"%{search_term.upper()}%"

    extra_filters = "\n        ".join(filters)
    query = _managed_users_base_query(extra_filters)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            permissions_map = _fetch_permissions_map(cursor)
            cursor.execute(query, **params)
            users: list[ManagedUser] = []
            seen_ids: set[int] = set()
            for row in cursor:
                data = _row_to_dict(cursor, row)
                user_id = data.get("id_usuario")
                if user_id is not None:
                    uid = int(user_id)
                    if uid in seen_ids:
                        continue
                    seen_ids.add(uid)

                username = _normalize_text(data.get("usuario"))
                app_ids = permissions_map.get(username.upper(), [])
                users.append(_build_managed_user(data, app_ids))
            return users


def get_managed_user(actor: dict, username: str) -> ManagedUser | None:
    params: dict = {"usuario": username.strip()}
    filters: list[str] = ["AND UPPER(TRIM(u.USUARIO)) = UPPER(TRIM(:usuario))"]

    if actor.get("portal_role") == "area_admin":
        filters.append("AND u.ID_AREA = :actor_area")
        params["actor_area"] = actor.get("id_area")

    extra_filters = "\n        ".join(filters)
    query = _managed_users_base_query(extra_filters)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, **params)
            row = cursor.fetchone()
            if not row:
                return None
            data = _row_to_dict(cursor, row)
            uname = _normalize_text(data.get("usuario"))
            app_ids = fetch_user_permission_ids(uname)
            return _build_managed_user(data, app_ids)


def _upsert_colaborador(
    cursor,
    num_id: str,
    email_personal: str,
    email_laboral: str,
    nombres: str,
) -> None:
    cursor.execute(
        """
        SELECT COLID FROM BDLIGA.INTRANET_COLABORADORES
        WHERE COLNID = :num_id
        """,
        num_id=num_id,
    )
    row = cursor.fetchone()
    if row:
        cursor.execute(
            """
            UPDATE BDLIGA.INTRANET_COLABORADORES
            SET COLEMAILP = :email_personal,
                COLEMAILL = :email_laboral
            WHERE COLID = :col_id
            """,
            email_personal=email_personal,
            email_laboral=email_laboral,
            col_id=row[0],
        )
        return

    col_id = _next_id(cursor, "INTRANET_COLABORADORES", "COLID")
    cursor.execute(
        """
        INSERT INTO BDLIGA.INTRANET_COLABORADORES
            (COLID, COLNID, COLNOM, COLEMAILP, COLEMAILL, COLES)
        VALUES
            (:col_id, :num_id, :nombres, :email_personal, :email_laboral, 1)
        """,
        col_id=col_id,
        num_id=num_id,
        nombres=nombres[:100],
        email_personal=email_personal,
        email_laboral=email_laboral,
    )


def _upsert_report_user(
    cursor,
    username: str,
    nombres: str,
    num_id: str,
    id_area: int,
    *,
    report_tipo: str = REPORT_TIPO_FALLBACK,
    password: str | None = None,
) -> None:
    """Actualiza reportes. Solo modifica CONTRASENA si password no es None."""
    safe_tipo = (_normalize_text(report_tipo).lower() or REPORT_TIPO_FALLBACK)[:10]
    if not safe_tipo:
        raise ValueError("El tipo de usuario en reportes es obligatorio")

    cursor.execute(
        """
        SELECT ID FROM BDLIGA.INTRANET_REPORT_USUARIOS
        WHERE IDNUM = :num_id
        """,
        num_id=num_id,
    )
    row = cursor.fetchone()
    if row:
        if password is not None:
            cursor.execute(
                """
                UPDATE BDLIGA.INTRANET_REPORT_USUARIOS
                SET USUARIO = :usuario,
                    CONTRASENA = :password,
                    NOMBRES = :nombres,
                    ESTADO = 1,
                    AREA = :area,
                    TIPO = :report_tipo
                WHERE ID = :report_id
                """,
                usuario=username,
                password=password,
                nombres=nombres,
                area=str(id_area),
                report_tipo=safe_tipo,
                report_id=row[0],
            )
        else:
            cursor.execute(
                """
                UPDATE BDLIGA.INTRANET_REPORT_USUARIOS
                SET USUARIO = :usuario,
                    NOMBRES = :nombres,
                    ESTADO = 1,
                    AREA = :area,
                    TIPO = :report_tipo
                WHERE ID = :report_id
                """,
                usuario=username,
                nombres=nombres,
                area=str(id_area),
                report_tipo=safe_tipo,
                report_id=row[0],
            )
        return

    if password is None:
        raise ValueError(
            "No existe registro en INTRANET_REPORT_USUARIOS para esta cédula. "
            "Indique una contraseña para crearlo."
        )

    report_id = _next_id(cursor, "INTRANET_REPORT_USUARIOS")
    cursor.execute(
        """
        INSERT INTO BDLIGA.INTRANET_REPORT_USUARIOS
            (ID, USUARIO, CONTRASENA, NOMBRES, ESTADO, IDNUM, AREA, TIPO)
        VALUES
            (:id, :usuario, :password, :nombres, 1, :num_id, :area, :report_tipo)
        """,
        id=report_id,
        usuario=username,
        password=password,
        nombres=nombres,
        num_id=num_id,
        area=str(id_area),
        report_tipo=safe_tipo,
    )


def _activate_apps(cursor, app_ids: list[int]) -> None:
    """Marca como activas todas las filas que comparten la misma URL."""
    url_keys: set[str] = set()
    for app_id in sorted(set(app_ids)):
        cursor.execute(
            """
            SELECT APUSLI FROM BDLIGA.INTRANET_APLICACIONES_USUARIOS
            WHERE APUSID = :app_id AND APUSLI IS NOT NULL
            """,
            app_id=app_id,
        )
        row = cursor.fetchone()
        if row and row[0]:
            url_keys.add(_normalize_url_key(_normalize_text(row[0])))

    for url_key in url_keys:
        cursor.execute(
            """
            UPDATE BDLIGA.INTRANET_APLICACIONES_USUARIOS
            SET PORTAL_ESTADO = 'activa'
            WHERE APUSLI IS NOT NULL
              AND LOWER(RTRIM(TRIM(APUSLI), '/')) = :url_key
            """,
            url_key=url_key,
        )


def _replace_permissions(cursor, username: str, app_ids: list[int]) -> None:
    cursor.execute(
        """
        DELETE FROM BDLIGA.INTRANET_APP_PERMISOS
        WHERE UPPER(TRIM(PERMUSU)) = UPPER(TRIM(:usuario))
        """,
        usuario=username,
    )
    for app_id in sorted(set(app_ids)):
        perm_id = _next_id(cursor, "INTRANET_APP_PERMISOS", "PERMIDE")
        cursor.execute(
            """
            INSERT INTO BDLIGA.INTRANET_APP_PERMISOS
                (PERMIDE, PERMAPP, PERMUSU, PERMMOD, PERMVIS)
            VALUES
                (:perm_id, :app_id, :usuario, 'S', 'S')
            """,
            perm_id=perm_id,
            app_id=app_id,
            usuario=username,
        )
    _activate_apps(cursor, app_ids)


def create_managed_user(actor: dict, payload: UserCreateRequest) -> ManagedUser:
    portal_role = payload.portal_role if payload.portal_role in PORTAL_ROLES else "usuario"
    _can_manage_target(actor, portal_role, payload.id_area)

    if actor.get("portal_role") == "area_admin":
        portal_role = "usuario"

    username = payload.username.strip()
    password = _validate_password(payload.password)
    report_tipo = _validate_report_tipo(payload.report_tipo, set(REPORT_TIPOS_KNOWN))

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1 FROM BDLIGA.INTRANET_USUARIOS
                WHERE UPPER(TRIM(USUARIO)) = UPPER(TRIM(:usuario))
                """,
                usuario=username,
            )
            if cursor.fetchone():
                raise ValueError("El usuario ya existe")

            user_id = _next_id(cursor, "INTRANET_USUARIOS")
            cursor.execute(
                """
                INSERT INTO BDLIGA.INTRANET_USUARIOS
                    (ID, USUARIO, CONTRASENA, NOMBRES, ID_CLASE, ESTADO, ID_AREA, NUM_ID, PORTAL_ROL)
                VALUES
                    (:id, :usuario, :password, :nombres, 0, 1, :id_area, :num_id, :portal_role)
                """,
                id=user_id,
                usuario=username,
                password=password[:INTRANET_PASSWORD_MAX],
                nombres=payload.nombres.strip(),
                id_area=payload.id_area,
                num_id=payload.num_id.strip(),
                portal_role=portal_role,
            )

            _upsert_report_user(
                cursor,
                username,
                payload.nombres.strip(),
                payload.num_id.strip(),
                payload.id_area,
                report_tipo=report_tipo,
                password=password,
            )
            _upsert_colaborador(
                cursor,
                payload.num_id.strip(),
                payload.email_personal.strip(),
                payload.email_laboral.strip(),
                payload.nombres.strip(),
            )
            _replace_permissions(cursor, username, payload.app_ids)
            conn.commit()

    created = get_managed_user(actor, username)
    if not created:
        raise RuntimeError("No se pudo recuperar el usuario creado")
    return created


def update_managed_user(actor: dict, username: str, payload: UserUpdateRequest) -> ManagedUser:
    current = get_managed_user(actor, username)
    if not current:
        raise LookupError("Usuario no encontrado")

    next_role = payload.portal_role if payload.portal_role else current.portal_role
    next_area = payload.id_area if payload.id_area is not None else current.id_area
    _can_manage_target(actor, next_role, next_area)

    if actor.get("portal_role") == "area_admin":
        if payload.portal_role in ("admin", "area_admin"):
            raise PermissionError("No puede cambiar el rol a administrador")
        next_role = current.portal_role if current.portal_role != "admin" else "usuario"

    with get_connection() as conn:
        with conn.cursor() as cursor:
            updates = []
            params: dict = {"usuario": username}

            if payload.nombres is not None:
                updates.append("NOMBRES = :nombres")
                params["nombres"] = payload.nombres.strip()
            if payload.num_id is not None:
                updates.append("NUM_ID = :num_id")
                params["num_id"] = payload.num_id.strip()
            if payload.id_area is not None:
                updates.append("ID_AREA = :id_area")
                params["id_area"] = payload.id_area
            if payload.portal_role is not None and actor.get("portal_role") == "admin":
                updates.append("PORTAL_ROL = :portal_role")
                params["portal_role"] = next_role
            if payload.password:
                validated_password = _validate_password(payload.password)
                updates.append("CONTRASENA = :password")
                params["password"] = validated_password[:INTRANET_PASSWORD_MAX]
            if payload.active is not None:
                updates.append("ESTADO = :estado")
                params["estado"] = "1" if payload.active else "0"

            if updates:
                cursor.execute(
                    f"""
                    UPDATE BDLIGA.INTRANET_USUARIOS
                    SET {", ".join(updates)}
                    WHERE UPPER(TRIM(USUARIO)) = UPPER(TRIM(:usuario))
                    """,
                    **params,
                )

            num_id = payload.num_id.strip() if payload.num_id else current.num_id
            nombres = payload.nombres.strip() if payload.nombres else current.nombres
            id_area = payload.id_area if payload.id_area is not None else current.id_area
            report_tipo = current.report_tipo
            if payload.report_tipo is not None:
                report_tipo = _validate_report_tipo(
                    payload.report_tipo,
                    set(REPORT_TIPOS_KNOWN),
                )

            report_profile_changed = (
                payload.nombres is not None
                or payload.num_id is not None
                or payload.id_area is not None
                or payload.password
                or payload.report_tipo is not None
            )
            if report_profile_changed:
                report_password = (
                    _validate_password(payload.password) if payload.password else None
                )
                _upsert_report_user(
                    cursor,
                    username,
                    nombres,
                    num_id,
                    int(id_area or 0),
                    report_tipo=report_tipo,
                    password=report_password,
                )

            if payload.email_personal is not None or payload.email_laboral is not None:
                _upsert_colaborador(
                    cursor,
                    num_id,
                    payload.email_personal if payload.email_personal is not None else current.email_personal,
                    payload.email_laboral if payload.email_laboral is not None else current.email_laboral,
                    nombres,
                )

            if payload.app_ids is not None:
                _replace_permissions(cursor, username, payload.app_ids)

            conn.commit()

    updated = get_managed_user(actor, username)
    if not updated:
        raise RuntimeError("No se pudo recuperar el usuario actualizado")
    return updated


def deactivate_managed_user(actor: dict, username: str) -> ManagedUser:
    return update_managed_user(actor, username, UserUpdateRequest(active=False))
