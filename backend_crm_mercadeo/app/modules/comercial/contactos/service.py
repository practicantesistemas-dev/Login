from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Contacto, ContactoEtiqueta
from app.modules.comercial.contactos.exceptions import ContactoNotFoundError
from app.modules.comercial.contactos.repository import ContactoRepository
from app.modules.comercial.contactos.schemas import ContactoCreate, ContactoRead
from app.modules.marketing.etiquetas.schemas import EtiquetaRead


def _to_read(contacto: Contacto) -> ContactoRead:
    datos = {
        "tipo_contacto": contacto.tipo_contacto,
        "tipo_documento": contacto.tipo_documento,
        "documento": contacto.documento,
        "nombre1": contacto.nombre1,
        "nombre2": contacto.nombre2,
        "apellido1": contacto.apellido1,
        "apellido2": contacto.apellido2,
        "sexo": contacto.sexo,
        "correo": contacto.correo,
        "telefono": contacto.telefono,
        "cargo": contacto.cargo,
        "municipio": contacto.municipio,
        "departamento": contacto.departamento,
        "fecha_nacimiento": contacto.fecha_nacimiento,
        "estado": contacto.estado,
        "empresa_id": contacto.empresa_id,
        "responsable_id": contacto.responsable_id,
    }
    return ContactoRead(
        id=contacto.id,
        fecha_creacion=contacto.fecha_creacion,
        fecha_actualizacion=contacto.fecha_actualizacion,
        etiquetas=[EtiquetaRead.model_validate(ce.etiqueta) for ce in contacto.etiquetas],
        **datos,
    )


class ContactoService:
    def __init__(self, db: Session) -> None:
        self.repository = ContactoRepository(db)

    def list(self, skip: int = 0, limit: int = 100) -> list[ContactoRead]:
        return [_to_read(contacto) for contacto in self.repository.list(skip=skip, limit=limit)]

    def get(self, contacto_id: int) -> ContactoRead:
        contacto = self.repository.get(contacto_id)
        if contacto is None:
            raise ContactoNotFoundError(contacto_id)
        return _to_read(contacto)

    def create(self, data: ContactoCreate, username: str) -> ContactoRead:
        etiqueta_ids = data.etiqueta_ids
        campos = data.model_dump(exclude={"etiqueta_ids"})
        contacto = Contacto(**campos)

        if etiqueta_ids:
            usuario_id = self.repository.obtener_usuario_id(username)
            ahora = datetime.now()
            for etiqueta_id in etiqueta_ids:
                contacto.etiquetas.append(
                    ContactoEtiqueta(
                        etiqueta_id=etiqueta_id, usuario_id=usuario_id, fecha=ahora
                    )
                )

        contacto = self.repository.create(contacto)
        return _to_read(contacto)
