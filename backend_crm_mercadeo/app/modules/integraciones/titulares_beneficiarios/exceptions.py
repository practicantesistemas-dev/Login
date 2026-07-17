from app.core.exceptions import NotFoundError


class TitularNotFoundError(NotFoundError):
    def __init__(self, id_titular: int) -> None:
        super().__init__(detail=f"Titular {id_titular} no encontrado")


class BeneficiarioNotFoundError(NotFoundError):
    def __init__(self, id_beneficiario: int) -> None:
        super().__init__(detail=f"Beneficiario {id_beneficiario} no encontrado")
