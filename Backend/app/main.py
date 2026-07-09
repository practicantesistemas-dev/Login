from contextlib import asynccontextmanager

import oracledb
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import close_db, init_db
from app.routers import admin, auth, pages, sso


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    mode = "Oracle BDLIGA" if settings.db_enabled else "JSON local"
    print(f"[Portal] Backend iniciado — modo: {mode} — puerto esperado: 5000")
    yield
    close_db()


app = FastAPI(
    title="Portal de Accesos — Fundación La Liga",
    description="API de autenticación y enlaces por usuario desde BDLIGA",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://160.2.1.80:3000",
        "http://160.2.1.80:5175",
        "http://0.0.0.0:3000",
        "http://0.0.0.0:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(pages.router, prefix=settings.api_prefix)
app.include_router(sso.router, prefix=settings.api_prefix)
app.include_router(admin.router, prefix=settings.api_prefix)


@app.exception_handler(oracledb.IntegrityError)
async def oracle_integrity_handler(_: Request, exc: oracledb.IntegrityError):
    message = str(exc)
    if "TIPO" in message and "ORA-01400" in message:
        detail = "Falta el tipo de usuario en reportes (SSO). Seleccione 'user' o 'root'."
    elif "ORA-01400" in message:
        detail = "Faltan datos obligatorios en la base de datos."
    elif "ORA-00001" in message:
        detail = "Ya existe un registro duplicado para ese usuario o cédula."
    else:
        detail = "No se pudo completar la operación en la base de datos."
    return JSONResponse(status_code=400, content={"detail": detail})


@app.exception_handler(oracledb.Error)
async def oracle_error_handler(_: Request, exc: oracledb.Error):
    message = str(exc)
    if "ORA-12170" in message or "TNS" in message.upper():
        detail = "No se pudo conectar con Oracle (tiempo de espera agotado). Verifique red/VPN e intente de nuevo."
    else:
        detail = "Error de base de datos. Intente de nuevo en unos segundos."
    return JSONResponse(status_code=503, content={"detail": detail})


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "db_enabled": settings.db_enabled,
        "version": "2.10-oracle-admin",
        "sso": True,
    }
