from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.servicios_proveedores.actividades.service import ActividadService


def get_actividad_service(db: Session = Depends(get_db)) -> ActividadService:
    return ActividadService(db)
