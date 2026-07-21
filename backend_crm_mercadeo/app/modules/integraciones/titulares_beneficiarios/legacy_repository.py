from sqlalchemy import text
from sqlalchemy.orm import Session


class LegacyRepository:
    """SQL crudo sobre tablas externas (INCLE, INTRANET_PREPLANLIGA) sin modelo ORM,
    usadas como efectos secundarios de activar/desactivar un titular."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def desmarcar_registros_incle(self, tipo: str, documento: str) -> int:
        stmt = text(
            """
            UPDATE INCLE
            SET CLEEST = 0
            WHERE CLEOBS = 'PLAN LIGA'
            AND CLETID = :tipo
            AND CLECED = :documento
            AND CLEEST = 1
            """
        )
        resultado = self.db.execute(stmt, {"tipo": tipo, "documento": documento})
        self.db.commit()
        return resultado.rowcount

    def marcar_registros_incle(self, tipo: str, documento: str) -> int:
        stmt = text(
            """
            UPDATE INCLE
            SET CLEEST = 1
            WHERE CLEOBS = 'PLAN LIGA'
            AND CLETID = :tipo
            AND CLECED = :documento
            AND CLEEST <> 1
            """
        )
        resultado = self.db.execute(stmt, {"tipo": tipo, "documento": documento})
        self.db.commit()
        return resultado.rowcount

    def desactivar_preplanliga(self, tipo: str, documento: str) -> int:
        stmt = text(
            """
            UPDATE INTRANET_PREPLANLIGA
            SET ESTADO = 'I'
            WHERE TIPO = :tipo AND DOCUMENTO = :documento
            """
        )
        resultado = self.db.execute(stmt, {"tipo": tipo, "documento": documento})
        self.db.commit()
        return resultado.rowcount
