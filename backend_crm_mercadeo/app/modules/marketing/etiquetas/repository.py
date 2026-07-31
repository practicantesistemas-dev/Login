from app.models import Etiqueta
from app.shared.database.base_repository import BaseRepository


class EtiquetaRepository(BaseRepository[Etiqueta]):
    model = Etiqueta
