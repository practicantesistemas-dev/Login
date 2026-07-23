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

    def crear_preplanliga(self, datos: dict) -> None:
        """Registra el alta en INTRANET_PREPLANLIGA (ESTADO 'R' = registrado).
        `datos` trae las llaves en mayuscula tal como llegan del schema TitularCrear."""
        stmt = text(
            """
            INSERT INTO INTRANET_PREPLANLIGA
            (TIPO_PLAN, TIPO, DOCUMENTO, NOMBRE1, NOMBRE2, APELLIDO1, APELLIDO2, FECHA_NACIMIENTO,
            SEXO, DIRECCION, CIUDAD, DEPARTAMENTO, CORREO, TELEFONO, EMPRESA, FECHA_REGISTRO, ESTADO)
            VALUES (:TIPO_PLAN, :TIPO_DOCUMENTO, :DOCUMENTO, :NOMBRE1, :NOMBRE2, :APELLIDO1, :APELLIDO2,
            :FECHA_NACIMIENTO, :SEXO, :DIRECCION, :CIUDAD, :DEPARTAMENTO, :CORREO, :TELEFONO, :EMPRESA,
            SYSDATE, 'R')
            """
        )
        self.db.execute(stmt, datos)
        self.db.commit()

    def existe_usuario_servinte(self, tipo: str, documento: str) -> bool:
        stmt = text("SELECT PACNOM FROM ABPAC WHERE PACTID = :tipo AND PACIDE = :documento")
        fila = self.db.execute(stmt, {"tipo": tipo, "documento": documento}).first()
        return bool(fila and fila[0])

    def crear_usuario_servinte(
        self,
        tipo: str,
        documento: str,
        nombre1: str,
        nombre2: str | None,
        apellido1: str,
        apellido2: str | None,
    ) -> bool:
        """Crea el usuario en Servinte (ABPAC/ABPACAUD/ABPACOTR) si no existe.
        Retorna True si se creo uno nuevo, False si ya existia."""
        if self.existe_usuario_servinte(tipo, documento):
            return False

        self.db.execute(
            text(
                """
                INSERT INTO ABPAC (PACIDE, PACTID, PACHIS, PACAP1, PACAP2, PACNOM, PACNO2, PACIDB)
                VALUES (:documento, :tipo, SQ_ABPAC_HIS.nextval, :apellido1, :apellido2, :nombre1, :nombre2, :documento)
                """
            ),
            {
                "documento": documento,
                "tipo": tipo,
                "apellido1": apellido1,
                "apellido2": apellido2,
                "nombre1": nombre1,
                "nombre2": nombre2,
            },
        )

        historia = self.db.execute(
            text("SELECT PACHIS FROM ABPAC WHERE PACTID = :tipo AND PACIDE = :documento"),
            {"tipo": tipo, "documento": documento},
        ).scalar()

        self.db.execute(
            text(
                """
                INSERT INTO ABPACAUD
                (PACAUDSEC, PACAUDUSU, PACAUDFAD, PACAUDUMO, PACAUDFMO, PACAUDEAD, PACAUDORI, PACAUDEAM)
                VALUES (:historia, 'dalopez', SYSDATE, null, null, '01', 'cinrep', '01')
                """
            ),
            {"historia": historia},
        )
        self.db.execute(
            text("INSERT INTO ABPACOTR (PACOTRSEC) VALUES (:historia)"),
            {"historia": historia},
        )

        self.db.commit()
        return True

    def existe_marca_incle(self, tipo: str, documento: str) -> bool:
        stmt = text("SELECT CLENOM FROM INCLE WHERE CLETID = :tipo AND CLECED = :documento")
        fila = self.db.execute(stmt, {"tipo": tipo, "documento": documento}).first()
        return bool(fila and fila[0])

    def marcar_nuevo_titular_incle(
        self, tipo: str, documento: str, nombre_completo: str
    ) -> bool:
        """Inscribe por primera vez al titular en INCLE + sedes (01, 03, 04).
        Retorna True si se marco, False si ya estaba marcado."""
        if self.existe_marca_incle(tipo, documento):
            return False

        stmt = text(
            """
            INSERT INTO INCLE (CLENRO, CLECED, CLETID, CLENOM, CLEDIR, CLETEL, CLEMED, CLEOBS, CLEEST, CLEUAD, CLEFAD)
            SELECT
                SQ_INCLE_NRO.NEXTVAL, DOCUMENTO, TIPO, :nombre_completo,
                DIRECCION, TELEFONO, '01', 'PLAN LIGA', '0', 'dalopez', SYSDATE
            FROM INTRANET_PLANLIGA
            WHERE DOCUMENTO = :documento AND TIPO = :tipo
            """
        )
        resultado = self.db.execute(
            stmt, {"nombre_completo": nombre_completo, "documento": documento, "tipo": tipo}
        )
        if resultado.rowcount == 0:
            return False

        for codigo in ("01", "03", "04"):
            self.db.execute(
                text(
                    """
                    INSERT INTO INCLEEAD (CLEEADTID, CLEEADCED, CLEEADEAD, CLEEADIND)
                    VALUES (:tipo, :documento, :codigo, 'S')
                    """
                ),
                {"tipo": tipo, "documento": documento, "codigo": codigo},
            )

        self.db.commit()
        return True

    def marcar_nuevo_beneficiario_incle(
        self, tipo: str, documento: str, nombre_completo: str
    ) -> bool:
        """Inscribe por primera vez al beneficiario en INCLE + sedes (01, 03, 04).
        Retorna True si se marco, False si ya estaba marcado."""
        if self.existe_marca_incle(tipo, documento):
            return False

        stmt = text(
            """
            INSERT INTO INCLE (CLENRO, CLECED, CLETID, CLENOM, CLEDIR, CLETEL, CLEMED, CLEOBS, CLEEST, CLEUAD, CLEFAD)
            SELECT
                SQ_INCLE_NRO.NEXTVAL, DOCUMENTO, TIPO, :nombre_completo,
                DIRECCION, TELEFONO, '01', 'PLAN LIGA', '0', 'dalopez', SYSDATE
            FROM INTRANET_PLANLIGA_BENEFICIARIO
            WHERE DOCUMENTO = :documento AND TIPO = :tipo
            """
        )
        resultado = self.db.execute(
            stmt, {"nombre_completo": nombre_completo, "documento": documento, "tipo": tipo}
        )
        if resultado.rowcount == 0:
            return False

        for codigo in ("01", "03", "04"):
            self.db.execute(
                text(
                    """
                    INSERT INTO INCLEEAD (CLEEADTID, CLEEADCED, CLEEADEAD, CLEEADIND)
                    VALUES (:tipo, :documento, :codigo, 'S')
                    """
                ),
                {"tipo": tipo, "documento": documento, "codigo": codigo},
            )

        self.db.commit()
        return True
