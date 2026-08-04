from app.core.exceptions import NotFoundError


class ProveedorNotFoundError(NotFoundError):
    def __init__(self, proveedor_id: int) -> None:
        super().__init__(detail=f"Proveedor {proveedor_id} no encontrado")
