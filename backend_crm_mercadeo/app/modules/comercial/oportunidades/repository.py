from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Contacto, Empresa, EtapaEmbudo, Oportunidad, PlanLiga, Usuario
from app.shared.database.base_repository import BaseRepository
from app.shared.enums import EtapaEmbudoNombre


class OportunidadRepository(BaseRepository[Oportunidad]):
    model = Oportunidad

    # Mismo patron que BitacoraRepository: se traen las filas relacionadas con outerjoin
    # (no relationships de SQLAlchemy) porque Oportunidad no declara relationship() hacia
    # Empresa/Contacto, solo hacia servicio/plan_liga_titular/responsable.
    def _query_base(self):
        return (
            select(Oportunidad, Empresa, Contacto, PlanLiga, Usuario, EtapaEmbudo)
            .outerjoin(Empresa, Oportunidad.empresa_id == Empresa.id)
            .outerjoin(Contacto, Oportunidad.contacto_id == Contacto.id)
            .outerjoin(PlanLiga, Oportunidad.plan_liga_titular_id == PlanLiga.id)
            .outerjoin(Usuario, Oportunidad.responsable_id == Usuario.id)
            .outerjoin(EtapaEmbudo, Oportunidad.etapa_id == EtapaEmbudo.id)
        )

    def listar(self, skip: int = 0, limit: int = 100) -> list:
        stmt = (
            self._query_base()
            .order_by(Oportunidad.fecha_creacion.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.execute(stmt).all())

    def obtener_con_relaciones(self, id_: int):
        stmt = self._query_base().where(Oportunidad.id == id_)
        return self.db.execute(stmt).first()

    def obtener_usuario_id(self, username: str) -> int | None:
        stmt = select(Usuario.id).where(
            func.upper(func.trim(Usuario.usuario)) == username.strip().upper()
        )
        return self.db.scalar(stmt)

    def obtener_etapa_id(self, nombre: EtapaEmbudoNombre) -> int | None:
        stmt = select(EtapaEmbudo.id).where(EtapaEmbudo.nombre == nombre)
        return self.db.scalar(stmt)
