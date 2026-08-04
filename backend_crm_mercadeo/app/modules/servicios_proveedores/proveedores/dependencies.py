from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.servicios_proveedores.proveedores.service import ProveedorService


def get_proveedor_service(db: Session = Depends(get_db)) -> ProveedorService:
    return ProveedorService(db)
