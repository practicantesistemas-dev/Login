from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.compartidos.ubicaciones.service import UbicacionesService


def get_ubicaciones_service(db: Session = Depends(get_db)) -> UbicacionesService:
    return UbicacionesService(db)
