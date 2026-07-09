"""Crea columna PORTAL_ROL y usuario admin en Oracle."""
from app.database import close_db, get_connection, init_db

REPORT_TIPO_DEFAULT = "user"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "12345"
ADMIN_NUM_ID = "123456789"
ADMIN_NOMBRES = "Administrador Portal"
PORTAL_ROL = "admin"


def _column_exists(cursor, column: str) -> bool:
    cursor.execute(
        """
        SELECT 1 FROM all_tab_columns
        WHERE owner = 'BDLIGA'
          AND table_name = 'INTRANET_USUARIOS'
          AND column_name = :col_name
        """,
        col_name=column.upper(),
    )
    return cursor.fetchone() is not None


def _find_sistemas_dep_id(cursor) -> int:
    cursor.execute(
        """
        SELECT DEPID FROM BDLIGA.INTRANET_DEPARTAMENTOS
        WHERE UPPER(TRIM(DEPDES)) LIKE '%SISTEMA%'
        ORDER BY DEPID
        FETCH FIRST 1 ROW ONLY
        """
    )
    row = cursor.fetchone()
    if not row:
        raise RuntimeError("No se encontró departamento Sistemas en INTRANET_DEPARTAMENTOS")
    return int(row[0])


def ensure_portal_rol_column(cursor) -> None:
    if _column_exists(cursor, "PORTAL_ROL"):
        print("PORTAL_ROL ya existe")
        return
    cursor.execute(
        """
        ALTER TABLE BDLIGA.INTRANET_USUARIOS
        ADD PORTAL_ROL VARCHAR2(20) DEFAULT 'usuario'
        """
    )
    print("Columna PORTAL_ROL creada")


def ensure_admin_user(cursor, dep_id: int) -> None:
    cursor.execute(
        """
        SELECT ID, PORTAL_ROL FROM BDLIGA.INTRANET_USUARIOS
        WHERE UPPER(TRIM(USUARIO)) = UPPER(TRIM(:usuario))
        """,
        usuario=ADMIN_USERNAME,
    )
    row = cursor.fetchone()

    if row:
        user_id = row[0]
        cursor.execute(
            """
            UPDATE BDLIGA.INTRANET_USUARIOS
            SET PORTAL_ROL = :rol,
                NOMBRES = :nombres,
                ID_AREA = :id_area,
                ESTADO = 1,
                CONTRASENA = :password
            WHERE ID = :user_id
            """,
            rol=PORTAL_ROL,
            nombres=ADMIN_NOMBRES,
            id_area=dep_id,
            password=ADMIN_PASSWORD,
            user_id=user_id,
        )
        print(f"Usuario admin actualizado (ID={user_id})")
    else:
        cursor.execute(
            """
            SELECT NVL(MAX(ID), 0) + 1 FROM BDLIGA.INTRANET_USUARIOS
            """
        )
        new_id = cursor.fetchone()[0]
        cursor.execute(
            """
            INSERT INTO BDLIGA.INTRANET_USUARIOS
                (ID, USUARIO, CONTRASENA, NOMBRES, ID_CLASE, ESTADO, ID_AREA, NUM_ID, PORTAL_ROL)
            VALUES
                (:id, :usuario, :password, :nombres, 0, 1, :id_area, :num_id, :rol)
            """,
            id=new_id,
            usuario=ADMIN_USERNAME,
            password=ADMIN_PASSWORD,
            nombres=ADMIN_NOMBRES,
            id_area=dep_id,
            num_id=ADMIN_NUM_ID,
            rol=PORTAL_ROL,
        )
        print(f"Usuario admin creado (ID={new_id})")

    cursor.execute(
        """
        SELECT ID FROM BDLIGA.INTRANET_REPORT_USUARIOS
        WHERE IDNUM = :num_id
        """,
        num_id=ADMIN_NUM_ID,
    )
    report_row = cursor.fetchone()
    if report_row:
        cursor.execute(
            """
            UPDATE BDLIGA.INTRANET_REPORT_USUARIOS
            SET USUARIO = :usuario,
                CONTRASENA = :password,
                NOMBRES = :nombres,
                ESTADO = 1
            WHERE ID = :report_id
            """,
            usuario=ADMIN_USERNAME,
            password=ADMIN_PASSWORD,
            nombres=ADMIN_NOMBRES,
            report_id=report_row[0],
        )
    else:
        cursor.execute(
            """
            SELECT NVL(MAX(ID), 0) + 1 FROM BDLIGA.INTRANET_REPORT_USUARIOS
            """
        )
        report_id = cursor.fetchone()[0]
        cursor.execute(
            """
            INSERT INTO BDLIGA.INTRANET_REPORT_USUARIOS
                (ID, USUARIO, CONTRASENA, NOMBRES, ESTADO, IDNUM, AREA, TIPO)
            VALUES
                (:id, :usuario, :password, :nombres, 1, :num_id, :area, :report_tipo)
            """,
            id=report_id,
            usuario=ADMIN_USERNAME,
            password=ADMIN_PASSWORD,
            nombres=ADMIN_NOMBRES,
            num_id=ADMIN_NUM_ID,
            area=str(dep_id),
            report_tipo=REPORT_TIPO_DEFAULT,
        )


def main() -> None:
    init_db()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        dep_id = _find_sistemas_dep_id(cursor)
        print(f"Departamento Sistemas: DEPID={dep_id}")
        ensure_portal_rol_column(cursor)
        ensure_admin_user(cursor, dep_id)
        conn.commit()
        print("Setup completado")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
        close_db()


if __name__ == "__main__":
    main()
