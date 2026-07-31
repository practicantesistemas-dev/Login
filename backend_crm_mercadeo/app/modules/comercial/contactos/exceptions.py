from app.core.exceptions import NotFoundError


class ContactoNotFoundError(NotFoundError):
    def __init__(self, contacto_id: int) -> None:
        super().__init__(detail=f"Contacto {contacto_id} no encontrado")
