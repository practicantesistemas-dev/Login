from sqlalchemy.orm import Session

from app.models import Etiqueta
from app.modules.marketing.etiquetas.repository import EtiquetaRepository
from app.modules.marketing.etiquetas.schemas import EtiquetaCreate


class EtiquetaService:
    def __init__(self, db: Session) -> None:
        self.repository = EtiquetaRepository(db)

    def list(self, skip: int = 0, limit: int = 100) -> list[Etiqueta]:
        return self.repository.list(skip=skip, limit=limit)

    def create(self, data: EtiquetaCreate) -> Etiqueta:
        etiqueta = Etiqueta(**data.model_dump())
        return self.repository.create(etiqueta)
