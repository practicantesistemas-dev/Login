from app.core.exceptions import NotFoundError


class ActividadNotFoundError(NotFoundError):
    def __init__(self, actividad_id: int) -> None:
        super().__init__(detail=f"Actividad {actividad_id} no encontrada")
