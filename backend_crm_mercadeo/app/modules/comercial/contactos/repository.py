from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.sql.elements import ColumnElement

from app.models import Contacto, ContactoEtiqueta, Empresa, Usuario
from app.shared.database.base_repository import BaseRepository
from app.shared.enums import TipoContacto


def _fecha_hace_anios(anios: int, hoy: date) -> date:
    try:
        return hoy.replace(year=hoy.year - anios)
    except ValueError:
        return hoy.replace(year=hoy.year - anios, day=28)


class ContactoRepository(BaseRepository[Contacto]):
    model = Contacto

    def obtener_usuario_id(self, username: str) -> int | None:
        stmt = select(Usuario.id).where(
            func.upper(func.trim(Usuario.usuario)) == username.strip().upper()
        )
        return self.db.scalar(stmt)

    def get_etiqueta_asociacion(
        self, contacto_id: int, etiqueta_id: int
    ) -> ContactoEtiqueta | None:
        return self.db.get(ContactoEtiqueta, (contacto_id, etiqueta_id))

    def _filtros(
        self,
        q: str | None,
        estado: str | None,
        ciudad: str | None,
        responsable_id: int | None,
        sexo: str | None,
        tipo_contacto: TipoContacto | None,
        edad_min: int | None,
        edad_max: int | None,
    ) -> list[ColumnElement]:
        condiciones = []
        if estado is not None:
            condiciones.append(Contacto.estado == estado)
        if ciudad is not None:
            condiciones.append(func.upper(Contacto.municipio) == ciudad.upper())
        if responsable_id is not None:
            condiciones.append(Contacto.responsable_id == responsable_id)
        if sexo is not None:
            condiciones.append(Contacto.sexo == sexo)
        if tipo_contacto is not None:
            condiciones.append(Contacto.tipo_contacto == tipo_contacto)
        if edad_min is not None:
            condiciones.append(Contacto.fecha_nacimiento <= _fecha_hace_anios(edad_min, date.today()))
        if edad_max is not None:
            condiciones.append(
                Contacto.fecha_nacimiento > _fecha_hace_anios(edad_max + 1, date.today())
            )
        if q:
            patron = f"%{q.strip().upper()}%"
            condiciones.append(
                or_(
                    func.upper(Contacto.nombre1).like(patron),
                    func.upper(Contacto.nombre2).like(patron),
                    func.upper(Contacto.apellido1).like(patron),
                    func.upper(Contacto.apellido2).like(patron),
                    func.upper(Contacto.documento).like(patron),
                    func.upper(Empresa.razon_social).like(patron),
                )
            )
        return condiciones

    def buscar(
        self,
        q: str | None = None,
        estado: str | None = None,
        ciudad: str | None = None,
        responsable_id: int | None = None,
        sexo: str | None = None,
        tipo_contacto: TipoContacto | None = None,
        edad_min: int | None = None,
        edad_max: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Contacto]:
        condiciones = self._filtros(
            q, estado, ciudad, responsable_id, sexo, tipo_contacto, edad_min, edad_max
        )
        stmt = (
            select(Contacto)
            .outerjoin(Empresa, Contacto.empresa_id == Empresa.id)
            .where(*condiciones)
            .order_by(Contacto.nombre1)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt))
