from enum import Enum


class EstadoBitacora(str, Enum):
    PENDIENTE = "pendiente"
    REALIZADO = "realizado"


class TipoContacto(str, Enum):
    CLIENTE = "Cliente"
    PROSPECTO = "Prospecto"
