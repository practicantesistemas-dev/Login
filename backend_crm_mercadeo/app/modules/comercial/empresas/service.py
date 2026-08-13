from sqlalchemy.orm import Session

from app.models import Empresa
from app.modules.comercial.empresas.exceptions import EmpresaNotFoundError
from app.modules.comercial.empresas.repository import EmpresaRepository
from app.modules.comercial.empresas.schemas import (
    EmpresaCreate,
    EmpresaUpdate,
    ImportacionEmpresasPlanLigaResultado,
)


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

    def create(self, data: EmpresaCreate, username: str) -> Empresa:
        usuario_id = self.repository.obtener_usuario_id(username)
        empresa = Empresa(**data.model_dump(), responsable_id=usuario_id)
        return self.repository.create(empresa)

    def update(self, empresa_id: int, data: EmpresaUpdate) -> Empresa:
        empresa = self.get(empresa_id)
        changes = data.model_dump(exclude_unset=True)
        return self.repository.update(empresa, changes)

    def delete(self, empresa_id: int) -> None:
        empresa = self.get(empresa_id)
        self.repository.delete(empresa)

    # Crea una Empresa (sin NIT: no existe en el origen) por cada nombre de
    # intranet_planliga.empresa que todavia no tenga una fila equivalente en
    # mercadeo_crm_empresas (comparando razon_social sin distinguir mayusculas/espacios).
    def importar_desde_plan_liga(self) -> ImportacionEmpresasPlanLigaResultado:
        existentes = self.repository.razones_sociales_existentes()
        creadas: list[str] = []
        for nombre in self.repository.nombres_empresa_planliga():
            clave = nombre.strip().upper()
            if clave in existentes:
                continue
            self.repository.db.add(Empresa(razon_social=nombre.strip(), estado=True))
            existentes.add(clave)
            creadas.append(nombre.strip())
        if creadas:
            self.repository.db.commit()
        return ImportacionEmpresasPlanLigaResultado(creadas=len(creadas), nombres=creadas)
