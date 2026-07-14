from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.comercial.empresas.service import EmpresaService


def get_empresa_service(db: Session = Depends(get_db)) -> EmpresaService:
    return EmpresaService(db)
