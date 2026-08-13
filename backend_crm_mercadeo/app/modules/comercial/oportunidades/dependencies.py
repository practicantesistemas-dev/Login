from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.comercial.oportunidades.service import OportunidadService


def get_oportunidad_service(db: Session = Depends(get_db)) -> OportunidadService:
    return OportunidadService(db)
