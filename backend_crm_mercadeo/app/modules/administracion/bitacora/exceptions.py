from app.core.exceptions import NotFoundError


class BitacoraNotFoundError(NotFoundError):
    def __init__(self, id_bitacora: int) -> None:
        super().__init__(detail=f"Registro de bitacora {id_bitacora} no encontrado")
