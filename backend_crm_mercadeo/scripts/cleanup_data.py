"""
Script de limpieza de datos de prueba del CRM de Mercadeo.

Elimina todo el contenido de las tablas propias mercadeo_crm_* (proveedores,
actividad, servicios, embudos, etapas, empresas, contactos, etiquetas,
contacto_etiqueta, campanas, segmentos, campana_segmento, oportunidades,
bitacora, titular_servicios, importaciones) en el orden correcto segun sus
llaves foraneas.

Las tablas intranet_usuarios e intranet_planliga son externas (modulos
Login/Integraciones) y NUNCA se tocan.

Uso (desde backend_crm_mercadeo, con el venv activado):

    python scripts/cleanup_data.py

Al terminar genera scripts/cleanup_data_log.txt con el detalle de cuantas
filas se eliminaron por tabla.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete

from app.database import SessionLocal
from app.models import (
    Actividad,
    Bitacora,
    Campana,
    CampanaSegmento,
    Contacto,
    ContactoEtiqueta,
    Embudo,
    Empresa,
    EtapaEmbudo,
    Etiqueta,
    Importacion,
    Oportunidad,
    Proveedor,
    Segmento,
    Servicio,
    TitularServicio,
)

LOG_PATH = Path(__file__).resolve().parent / "cleanup_data_log.txt"

# Orden de borrado: hijos antes que padres (inverso al orden de insercion
# usado en seed_data.py). Solo tablas propias de mercadeo_crm_*;
# intranet_usuarios e intranet_planliga son externas y nunca se tocan.
CLEANUP_MODELS = [
    Importacion,
    TitularServicio,
    Bitacora,
    Oportunidad,
    CampanaSegmento,
    Segmento,
    Campana,
    ContactoEtiqueta,
    Etiqueta,
    Contacto,
    Empresa,
    EtapaEmbudo,
    Embudo,
    Servicio,
    Actividad,
    Proveedor,
]


def main() -> None:
    db = SessionLocal()
    log_lines: list[str] = []

    def log(line: str = "") -> None:
        print(line)
        log_lines.append(line)

    try:
        log("=== Limpieza de datos de prueba - CRM Mercadeo ===")
        log(f"Fecha de ejecucion: {datetime.now(timezone.utc).isoformat()}")
        log("")

        for model in CLEANUP_MODELS:
            result = db.execute(delete(model))
            log(f"  {model.__tablename__}: {result.rowcount} fila(s) eliminada(s)")

        db.commit()
        log("")
        log("Limpieza completada correctamente.")

    except Exception:
        db.rollback()
        log("")
        log("ERROR: la limpieza fallo y se hizo rollback. Revisa el traceback en consola.")
        raise
    finally:
        db.close()
        LOG_PATH.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        print(f"\nLog escrito en: {LOG_PATH}")


if __name__ == "__main__":
    main()
