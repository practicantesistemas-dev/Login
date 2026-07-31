from sqlalchemy import func, select

from app.models import Contacto, Usuario
from app.shared.database.base_repository import BaseRepository


class ContactoRepository(BaseRepository[Contacto]):
    model = Contacto

    def obtener_usuario_id(self, username: str) -> int | None:
        stmt = select(Usuario.id).where(
            func.upper(func.trim(Usuario.usuario)) == username.strip().upper()
        )
        return self.db.scalar(stmt)
