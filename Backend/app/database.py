import oracledb

from app.config import settings

pool: oracledb.ConnectionPool | None = None


def init_db() -> None:
    global pool
    if not settings.db_enabled:
        return

    try:
        oracledb.init_oracle_client()
    except Exception:
        pass

    pool = oracledb.create_pool(
        user=settings.scse_db_user,
        password=settings.scse_db_passwd,
        host=settings.scse_db_ip,
        port=settings.scse_db_port,
        service_name=settings.scse_db_database,
        min=1,
        max=8,
        increment=1,
        timeout=30,
        tcp_connect_timeout=20.0,
    )


def close_db() -> None:
    global pool
    if pool:
        pool.close(force=True)
        pool = None


def get_connection():
    if pool is None:
        raise RuntimeError("La base de datos no está configurada o no se pudo conectar.")
    try:
        return pool.acquire()
    except oracledb.Error as exc:
        message = str(exc)
        if "ORA-12170" in message or "TNS" in message.upper():
            raise RuntimeError(
                "No se pudo conectar con Oracle (tiempo de espera agotado). "
                "Verifique red/VPN e intente de nuevo."
            ) from exc
        raise
