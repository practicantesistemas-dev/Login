from enum import Enum


class EstadoBitacora(str, Enum):
    PENDIENTE = "pendiente"
    REALIZADO = "realizado"


class TipoActividadBitacora(str, Enum):
    LLAMADA = "llamada"
    CORREO = "correo"
    REUNION = "reunion"
    WHATSAPP = "whatsapp"
    NOTA = "nota"


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
