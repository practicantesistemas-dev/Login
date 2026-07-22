from app.core.exceptions import ConflictError, NotFoundError


class TitularNotFoundError(NotFoundError):
    def __init__(self, id_titular: int) -> None:
        super().__init__(detail=f"Titular {id_titular} no encontrado")


class BeneficiarioNotFoundError(NotFoundError):
    def __init__(self, id_beneficiario: int) -> None:
        super().__init__(detail=f"Beneficiario {id_beneficiario} no encontrado")


class TitularInactivoError(ConflictError):
    def __init__(self, id_titular: int) -> None:
        super().__init__(
            detail=(
                f"No se pudo activar el beneficiario ya que el titular "
                f"{id_titular} esta inactivo"
            )
        )
