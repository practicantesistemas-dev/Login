from enum import Enum


class EstadoBitacora(str, Enum):
    PENDIENTE = "pendiente"
    REALIZADO = "realizado"


class TipoContacto(str, Enum):
    CLIENTE = "Cliente"
    PROSPECTO = "Prospecto"


class EtapaEmbudoNombre(str, Enum):
    LEAD = "Lead"
    PRIMER_CONTACTO = "Primer Contacto"
    REUNION = "Reunión"
    COTIZACION = "Cotización"
    NEGOCIACION = "Negociación"
    GANADA = "Ganada"
    PERDIDA = "Perdida"
