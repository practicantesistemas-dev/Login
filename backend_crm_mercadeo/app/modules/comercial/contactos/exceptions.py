from app.core.exceptions import NotFoundError


class ContactoNotFoundError(NotFoundError):
    def __init__(self, contacto_id: int) -> None:
        super().__init__(detail=f"Contacto {contacto_id} no encontrado")


class ContactoEtiquetaNotFoundError(NotFoundError):
    def __init__(self, contacto_id: int, etiqueta_id: int) -> None:
        super().__init__(
            detail=f"La etiqueta {etiqueta_id} no está asociada al contacto {contacto_id}"
        )
