from app.core.exceptions import NotFoundError


class EmpresaNotFoundError(NotFoundError):
    def __init__(self, empresa_id: int) -> None:
        super().__init__(detail=f"Empresa {empresa_id} no encontrada")
