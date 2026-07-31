from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.comercial.contactos.service import ContactoService


def get_contacto_service(db: Session = Depends(get_db)) -> ContactoService:
    return ContactoService(db)
