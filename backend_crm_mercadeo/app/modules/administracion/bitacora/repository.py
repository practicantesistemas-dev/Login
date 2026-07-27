from app.models import Bitacora
from app.shared.database.base_repository import BaseRepository


class BitacoraRepository(BaseRepository[Bitacora]):
    model = Bitacora
