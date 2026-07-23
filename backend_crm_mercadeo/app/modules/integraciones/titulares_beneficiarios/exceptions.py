from app.core.exceptions import ConflictError, NotFoundError


class TitularNotFoundError(NotFoundError):
    def __init__(self, id_titular: int) -> None:
        super().__init__(detail=f"Titular {id_titular} no encontrado")


class BeneficiarioNotFoundError(NotFoundError):
    def __init__(self, id_beneficiario: int) -> None:
        super().__init__(detail=f"Beneficiario {id_beneficiario} no encontrado")


class TitularInactivoError(ConflictError):
    def __init__(self, id_titular: int, accion: str = "activar el beneficiario") -> None:
        super().__init__(
            detail=(
                f"No se pudo {accion} ya que el titular "
                f"{id_titular} esta inactivo"
            )
        )


class DocumentoDuplicadoError(ConflictError):
    def __init__(self, documento: str, tipo_registro: str) -> None:
        super().__init__(
            detail=(
                f"El documento {documento} ya esta registrado como "
                f"{tipo_registro.lower()}"
            )
        )


class CupoBeneficiariosExcedidoError(ConflictError):
    def __init__(self, id_titular: int) -> None:
        super().__init__(
            detail=(
                f"El titular {id_titular} ya alcanzo el cupo maximo de "
                f"beneficiarios de su plan"
            )
        )
