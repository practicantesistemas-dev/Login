from sqlalchemy.orm import Session

from app.models import Bitacora
from app.modules.administracion.bitacora.repository import BitacoraRepository
from app.modules.administracion.bitacora.schemas import BitacoraCreate


class BitacoraService:
    def __init__(self, db: Session) -> None:
        self.repository = BitacoraRepository(db)

    def create(self, data: BitacoraCreate) -> Bitacora:
        bitacora = Bitacora(**data.model_dump())
        return self.repository.create(bitacora)
