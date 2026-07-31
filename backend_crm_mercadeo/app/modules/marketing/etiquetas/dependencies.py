from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.marketing.etiquetas.service import EtiquetaService


def get_etiqueta_service(db: Session = Depends(get_db)) -> EtiquetaService:
    return EtiquetaService(db)
