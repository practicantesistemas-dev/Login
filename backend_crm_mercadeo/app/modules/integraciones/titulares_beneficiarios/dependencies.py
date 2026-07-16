from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.integraciones.titulares_beneficiarios.service import (
    TitularesBeneficiariosService,
)


def get_titulares_beneficiarios_service(
    db: Session = Depends(get_db),
) -> TitularesBeneficiariosService:
    return TitularesBeneficiariosService(db)
