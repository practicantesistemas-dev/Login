from fastapi import FastAPI

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import setup_middlewares
from app.modules.comercial.empresas.router import router as empresas_router
from app.modules.comercial.tablero.router import router as tablero_router
from app.modules.integraciones.titulares_beneficiarios.router import (
    router as titulares_beneficiarios_router,
)

setup_logging()

app = FastAPI(title=settings.app_name)

setup_middlewares(app)
register_exception_handlers(app)

app.include_router(empresas_router, prefix=settings.api_prefix)
app.include_router(tablero_router, prefix=settings.api_prefix)
app.include_router(titulares_beneficiarios_router, prefix=settings.api_prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}
