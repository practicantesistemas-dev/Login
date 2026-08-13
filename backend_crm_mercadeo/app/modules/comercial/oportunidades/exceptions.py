from app.core.exceptions import NotFoundError


class OportunidadNotFoundError(NotFoundError):
    def __init__(self, oportunidad_id: int) -> None:
        super().__init__(detail=f"Oportunidad {oportunidad_id} no encontrada")


class EtapaEmbudoNoConfiguradaError(NotFoundError):
    def __init__(self, nombre: str) -> None:
        super().__init__(
            detail=(
                f"La etapa '{nombre}' no esta configurada en mercadeo_crm_etapas_embudo "
                "(revisa el embudo comercial)."
            )
        )
