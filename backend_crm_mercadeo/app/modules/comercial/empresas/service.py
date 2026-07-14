from sqlalchemy.orm import Session

from app.models import Empresa
from app.modules.comercial.empresas.exceptions import EmpresaNotFoundError
from app.modules.comercial.empresas.repository import EmpresaRepository
from app.modules.comercial.empresas.schemas import EmpresaCreate, EmpresaUpdate


class EmpresaService:
    def __init__(self, db: Session) -> None:
        self.repository = EmpresaRepository(db)

    def list(self, skip: int = 0, limit: int = 100) -> list[Empresa]:
        return self.repository.list(skip=skip, limit=limit)

    def get(self, empresa_id: int) -> Empresa:
        empresa = self.repository.get(empresa_id)
        if empresa is None:
            raise EmpresaNotFoundError(empresa_id)
        return empresa

    def create(self, data: EmpresaCreate) -> Empresa:
        empresa = Empresa(**data.model_dump())
        return self.repository.create(empresa)

    def update(self, empresa_id: int, data: EmpresaUpdate) -> Empresa:
        empresa = self.get(empresa_id)
        changes = data.model_dump(exclude_unset=True)
        return self.repository.update(empresa, changes)

    def delete(self, empresa_id: int) -> None:
        empresa = self.get(empresa_id)
        self.repository.delete(empresa)
