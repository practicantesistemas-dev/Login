from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.administracion.bitacora.service import BitacoraService


def get_bitacora_service(db: Session = Depends(get_db)) -> BitacoraService:
    return BitacoraService(db)
