from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Contacto, ContactoEtiqueta
from app.modules.comercial.contactos.exceptions import (
    ContactoEtiquetaNotFoundError,
    ContactoNotFoundError,
)
from app.modules.comercial.contactos.repository import ContactoRepository
from app.modules.comercial.contactos.schemas import (
    ContactoCreate,
    ContactoEmpresaResumen,
    ContactoRead,
    ContactoResponsableResumen,
)
from app.modules.marketing.etiquetas.schemas import EtiquetaRead
from app.shared.enums import TipoContacto


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
        empresa=(
            ContactoEmpresaResumen.model_validate(contacto.empresa)
            if contacto.empresa is not None
            else None
        ),
        responsable=(
            ContactoResponsableResumen.model_validate(contacto.responsable)
            if contacto.responsable is not None
            else None
        ),
        **datos,
    )


class ContactoService:
    def __init__(self, db: Session) -> None:
        self.repository = ContactoRepository(db)

    def list(
        self,
        q: str | None = None,
        estado: str | None = None,
        municipio: str | None = None,
        departamento: str | None = None,
        responsable_id: int | None = None,
        sexo: str | None = None,
        tipo_contacto: TipoContacto | None = None,
        edad_min: int | None = None,
        edad_max: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ContactoRead]:
        contactos = self.repository.buscar(
            q=q,
            estado=estado,
            municipio=municipio,
            departamento=departamento,
            responsable_id=responsable_id,
            sexo=sexo,
            tipo_contacto=tipo_contacto,
            edad_min=edad_min,
            edad_max=edad_max,
            skip=skip,
            limit=limit,
        )
        return [_to_read(contacto) for contacto in contactos]

    def get(self, contacto_id: int) -> ContactoRead:
        contacto = self.repository.get(contacto_id)
        if contacto is None:
            raise ContactoNotFoundError(contacto_id)
        return _to_read(contacto)

    def create(self, data: ContactoCreate, username: str) -> ContactoRead:
        etiqueta_ids = data.etiqueta_ids
        campos = data.model_dump(exclude={"etiqueta_ids"})
        usuario_id = self.repository.obtener_usuario_id(username)
        contacto = Contacto(**campos, responsable_id=usuario_id)

        if etiqueta_ids:
            ahora = datetime.now()
            for etiqueta_id in etiqueta_ids:
                contacto.etiquetas.append(
                    ContactoEtiqueta(
                        etiqueta_id=etiqueta_id, usuario_id=usuario_id, fecha=ahora
                    )
                )

        contacto = self.repository.create(contacto)
        return _to_read(contacto)

    def eliminar_etiqueta(self, contacto_id: int, etiqueta_id: int) -> None:
        asociacion = self.repository.get_etiqueta_asociacion(contacto_id, etiqueta_id)
        if asociacion is None:
            raise ContactoEtiquetaNotFoundError(contacto_id, etiqueta_id)
        self.repository.delete(asociacion)

    def delete(self, contacto_id: int) -> None:
        contacto = self.repository.get(contacto_id)
        if contacto is None:
            raise ContactoNotFoundError(contacto_id)
        self.repository.delete(contacto)
