from app.models import Empresa
from app.shared.database.base_repository import BaseRepository


class EmpresaRepository(BaseRepository[Empresa]):
    model = Empresa
