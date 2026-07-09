"""Agrega PORTAL_ESTADO a aplicaciones (activa / inactiva)."""
from app.database import close_db, get_connection, init_db

COLUMN_NAME = "PORTAL_ESTADO"
DEFAULT_VALUE = "inactiva"


def _column_exists(cursor) -> bool:
    cursor.execute(
        """
        SELECT 1 FROM all_tab_columns
        WHERE owner = 'BDLIGA'
          AND table_name = 'INTRANET_APLICACIONES_USUARIOS'
          AND column_name = :col_name
        """,
        col_name=COLUMN_NAME,
    )
    return cursor.fetchone() is not None


def ensure_portal_estado_column(cursor) -> None:
    if _column_exists(cursor):
        print(f"{COLUMN_NAME} ya existe")
        return
    cursor.execute(
        f"""
        ALTER TABLE BDLIGA.INTRANET_APLICACIONES_USUARIOS
        ADD {COLUMN_NAME} VARCHAR2(10) DEFAULT '{DEFAULT_VALUE}'
        """
    )
    print(f"Columna {COLUMN_NAME} creada")


def set_all_inactiva(cursor) -> None:
    cursor.execute(
        f"""
        UPDATE BDLIGA.INTRANET_APLICACIONES_USUARIOS
        SET {COLUMN_NAME} = :estado
        WHERE {COLUMN_NAME} IS NULL OR TRIM({COLUMN_NAME}) = ''
        """,
        estado=DEFAULT_VALUE,
    )
    print(f"Filas inicializadas a '{DEFAULT_VALUE}':", cursor.rowcount)


def main() -> None:
    init_db()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        ensure_portal_estado_column(cursor)
        set_all_inactiva(cursor)
        conn.commit()
        print("Setup PORTAL_ESTADO completado")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
        close_db()


if __name__ == "__main__":
    main()
