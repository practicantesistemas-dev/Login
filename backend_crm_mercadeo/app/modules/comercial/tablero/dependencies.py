from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.comercial.tablero.service import TableroService


def get_tablero_service(db: Session = Depends(get_db)) -> TableroService:
    return TableroService(db)
