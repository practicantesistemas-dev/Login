"""
Script de datos de prueba para el CRM de Mercadeo.

Inserta un pequeno conjunto de registros de ejemplo en las tablas
mercadeo_crm_* (proveedores, servicios, empresas, contactos, etiquetas,
campanas, segmentos, oportunidades, bitacora, titular_servicios,
importaciones, etc.) respetando el orden de dependencias por llave
foranea.

Las tablas intranet_usuarios e intranet_planliga son externas (modulos
Login/Integraciones) y NO se modifican: el script solo lee el primer
usuario y el primer titular de plan liga existentes para usarlos como
responsable_id / usuario_id / titular_id en los registros de prueba, de
forma que quede una relacion real (ej. una bitacora o una etiqueta
asociada a un usuario). Si no encuentra ninguno, deja esas columnas en
NULL (son nullable) y lo indica en el log.

Uso (desde backend_crm_mercadeo, con el venv activado):

    python scripts/seed_data.py

Al terminar genera scripts/seed_data_log.txt con el detalle de lo
insertado (tabla, id generado y datos principales) para poder rastrear
o limpiar despues los registros de prueba.
"""

import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete, select

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
    PlanLiga,
    Proveedor,
    Segmento,
    Servicio,
    TitularServicio,
    Usuario,
)

LOG_PATH = Path(__file__).resolve().parent / "seed_data_log.txt"

# Orden de borrado: hijos antes que padres (inverso al orden de insercion).
# Solo tablas propias de mercadeo_crm_*; intranet_usuarios e
# intranet_planliga son externas y nunca se tocan.
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


def cleanup(db, log) -> None:
    log("Limpiando datos de prueba insertados en ejecuciones anteriores...")
    for model in CLEANUP_MODELS:
        result = db.execute(delete(model))
        log(f"  {model.__tablename__}: {result.rowcount} fila(s) eliminada(s)")
    db.commit()
    log("")


def main() -> None:
    db = SessionLocal()
    log_lines: list[str] = []

    def log(line: str = "") -> None:
        print(line)
        log_lines.append(line)

    try:
        log("=== Seed de datos de prueba - CRM Mercadeo ===")
        log(f"Fecha de ejecucion: {datetime.now(timezone.utc).isoformat()}")
        log("")

        cleanup(db, log)

        usuario_id = db.scalar(select(Usuario.id).order_by(Usuario.id).limit(1))
        planliga_id = db.scalar(select(PlanLiga.id).order_by(PlanLiga.id).limit(1))

        if usuario_id is None:
            log("AVISO: no se encontro ningun registro en intranet_usuarios; "
                "los campos usuario_id/responsable_id quedaran en NULL.")
        else:
            log(f"Usando intranet_usuarios.id = {usuario_id} para las relaciones de usuario.")

        if planliga_id is None:
            log("AVISO: no se encontro ningun registro en intranet_planliga; "
                "los campos titular_id/plan_liga_titular_id/planliga_id quedaran en NULL.")
        else:
            log(f"Usando intranet_planliga.id = {planliga_id} para las relaciones de titular.")

        log("")

        # --- Proveedores -----------------------------------------------
        proveedor1 = Proveedor(
            nombre="Proveedor Insumos Medicos SAS",
            categoria="Insumos",
            nit="900123456-1",
            correo="contacto@insumosmedicos.com",
            telefono="3001234567",
            estado=True,
        )
        proveedor2 = Proveedor(
            nombre="Eventos y Logistica LTDA",
            categoria="Eventos",
            nit="900654321-2",
            correo="ventas@eventoslogistica.com",
            telefono="3009876543",
            estado=True,
        )
        db.add_all([proveedor1, proveedor2])
        db.flush()

        # --- Actividad (depende de Proveedores) -------------------------
        actividad1 = Actividad(
            nombre="Alquiler de stand",
            cantidad=1,
            precio=1500000.0,
            descripcion="Stand para feria de salud",
            proveedor_id=proveedor1.id,
        )
        actividad2 = Actividad(
            nombre="Catering evento",
            cantidad=50,
            precio=25000.0,
            descripcion="Refrigerios para 50 personas",
            proveedor_id=proveedor2.id,
        )
        db.add_all([actividad1, actividad2])

        # --- Servicios (responsable_id -> intranet_usuarios) ------------
        servicio1 = Servicio(
            nombre="Consulta Oncologica General",
            categoria="Consulta",
            tipo="Presencial",
            max_beneficiarios=1,
            estado=True,
            descripcion="Consulta con especialista en oncologia",
            responsable_id=usuario_id,
        )
        servicio2 = Servicio(
            nombre="Taller Prevencion Cancer de Mama",
            categoria="Taller",
            tipo="Grupal",
            max_beneficiarios=30,
            estado=True,
            descripcion="Taller educativo de prevencion",
            responsable_id=usuario_id,
        )
        db.add_all([servicio1, servicio2])
        db.flush()

        # --- Embudos y Etapas --------------------------------------------
        embudo1 = Embudo(
            nombre="Embudo Comercial Servicios",
            descripcion="Embudo de ventas para servicios oncologicos",
        )
        db.add(embudo1)
        db.flush()

        etapa1 = EtapaEmbudo(embudo_id=embudo1.id, nombre="Contacto inicial", orden=1)
        etapa2 = EtapaEmbudo(embudo_id=embudo1.id, nombre="Propuesta enviada", orden=2)
        etapa3 = EtapaEmbudo(embudo_id=embudo1.id, nombre="Cierre", orden=3)
        db.add_all([etapa1, etapa2, etapa3])
        db.flush()

        # --- Empresas (responsable_id -> intranet_usuarios) --------------
        empresa1 = Empresa(
            razon_social="Clinica Vida Sana SAS",
            nit="800111222-3",
            industria="Salud",
            direccion="Cra 45 #12-34",
            ciudad="Bogota",
            estado=True,
            responsable_id=usuario_id,
        )
        empresa2 = Empresa(
            razon_social="Fundacion Bienestar Total",
            nit="800333444-5",
            industria="ONG",
            direccion="Calle 10 #5-67",
            ciudad="Medellin",
            estado=True,
            responsable_id=usuario_id,
        )
        db.add_all([empresa1, empresa2])
        db.flush()

        # --- Contactos (empresa_id, responsable_id) -----------------------
        contacto1 = Contacto(
            tipo_contacto="Cliente",
            tipo_documento="CC",
            documento="1000123456",
            nombre1="Laura",
            apellido1="Gomez",
            sexo="F",
            correo="laura.gomez@example.com",
            telefono="3101234567",
            cargo="Gerente",
            ciudad="Bogota",
            estado="Activo",
            empresa_id=empresa1.id,
            responsable_id=usuario_id,
        )
        contacto2 = Contacto(
            tipo_contacto="Prospecto",
            tipo_documento="CC",
            documento="1000654321",
            nombre1="Carlos",
            apellido1="Ramirez",
            sexo="M",
            correo="carlos.ramirez@example.com",
            telefono="3117654321",
            cargo="Director",
            ciudad="Medellin",
            estado="Activo",
            empresa_id=empresa2.id,
            responsable_id=usuario_id,
        )
        contacto3 = Contacto(
            tipo_contacto="Cliente",
            tipo_documento="CC",
            documento="1000998877",
            nombre1="Maria",
            apellido1="Torres",
            sexo="F",
            correo="maria.torres@example.com",
            telefono="3123456789",
            cargo="Coordinadora",
            ciudad="Bogota",
            estado="Activo",
            empresa_id=empresa1.id,
            responsable_id=usuario_id,
        )
        db.add_all([contacto1, contacto2, contacto3])
        db.flush()

        # --- Etiquetas + ContactoEtiqueta (usuario_id) --------------------
        etiqueta1 = Etiqueta(nombre="VIP", color="#FFD700")
        etiqueta2 = Etiqueta(nombre="Seguimiento", color="#1E90FF")
        db.add_all([etiqueta1, etiqueta2])
        db.flush()

        ahora = datetime.now(timezone.utc)

        contacto_etiqueta1 = ContactoEtiqueta(
            contacto_id=contacto1.id,
            etiqueta_id=etiqueta1.id,
            usuario_id=usuario_id,
            fecha=ahora,
        )
        contacto_etiqueta2 = ContactoEtiqueta(
            contacto_id=contacto2.id,
            etiqueta_id=etiqueta2.id,
            usuario_id=usuario_id,
            fecha=ahora,
        )
        db.add_all([contacto_etiqueta1, contacto_etiqueta2])

        # --- Campanas y Segmentos ------------------------------------------
        campana1 = Campana(
            nombre="Campana Prevencion Cancer 2026",
            asunto="Cuida tu salud, hazte el chequeo",
            contenido="Contenido de ejemplo de la campana de prevencion.",
            estado="Activa",
            fecha_inicio=date(2026, 1, 15),
            fecha_fin=date(2026, 3, 15),
        )
        campana2 = Campana(
            nombre="Campana Fidelizacion Clientes",
            asunto="Beneficios exclusivos para ti",
            contenido="Contenido de ejemplo de la campana de fidelizacion.",
            estado="Programada",
            fecha_inicio=date(2026, 8, 1),
            fecha_fin=date(2026, 9, 30),
        )
        db.add_all([campana1, campana2])

        segmento1 = Segmento(
            nombre="Clientes Bogota",
            filtros='{"ciudad": "Bogota"}',
            fecha_creacion=ahora,
            usuario_id=usuario_id or 0,
        )
        segmento2 = Segmento(
            nombre="Prospectos Activos",
            filtros='{"estado": "Activo", "tipo_contacto": "Prospecto"}',
            fecha_creacion=ahora,
            usuario_id=usuario_id or 0,
        )
        db.add_all([segmento1, segmento2])
        db.flush()

        campana_segmento1 = CampanaSegmento(
            campana_id=campana1.id,
            segmento_id=segmento1.id,
            usuario_id=usuario_id,
            fecha=ahora,
        )
        campana_segmento2 = CampanaSegmento(
            campana_id=campana2.id,
            segmento_id=segmento2.id,
            usuario_id=usuario_id,
            fecha=ahora,
        )
        db.add_all([campana_segmento1, campana_segmento2])

        # --- Oportunidades ----------------------------------------------
        oportunidad1 = Oportunidad(
            empresa_id=empresa1.id,
            contacto_id=contacto1.id,
            servicio_id=servicio1.id,
            etapa_id=etapa1.id,
            responsable_id=usuario_id,
            valor=3500000.0,
            probabilidad=70.0,
            estado="Abierta",
            plan_liga_titular_id=planliga_id,
        )
        oportunidad2 = Oportunidad(
            empresa_id=empresa2.id,
            contacto_id=contacto2.id,
            servicio_id=servicio2.id,
            etapa_id=etapa2.id,
            responsable_id=usuario_id,
            valor=1200000.0,
            probabilidad=40.0,
            estado="Abierta",
            plan_liga_titular_id=planliga_id,
        )
        db.add_all([oportunidad1, oportunidad2])
        db.flush()

        # --- Bitacora (usuario_id, titular_id) ----------------------------
        bitacora1 = Bitacora(
            usuario_id=usuario_id,
            contacto_id=contacto1.id,
            empresa_id=empresa1.id,
            oportunidad_id=oportunidad1.id,
            titular_id=planliga_id,
            tipo="Llamada",
            descripcion="Se contacto al cliente para agendar consulta",
            proximo_paso="Enviar cotizacion",
            fecha=ahora,
        )
        bitacora2 = Bitacora(
            usuario_id=usuario_id,
            contacto_id=contacto2.id,
            empresa_id=empresa2.id,
            oportunidad_id=oportunidad2.id,
            titular_id=planliga_id,
            tipo="Reunion",
            descripcion="Reunion inicial de presentacion de servicios",
            proximo_paso="Seguimiento en una semana",
            fecha=ahora,
        )
        db.add_all([bitacora1, bitacora2])

        # --- Titular de servicios (planliga_id, servicio_id) --------------
        titular_servicio1 = TitularServicio(
            planliga_id=planliga_id,
            servicio_id=servicio1.id,
            fecha_asignacion=ahora,
            estado="Activo",
            observaciones="Asignacion de prueba",
        )
        titular_servicio2 = TitularServicio(
            planliga_id=planliga_id,
            servicio_id=servicio2.id,
            fecha_asignacion=ahora,
            estado="Activo",
            observaciones="Asignacion de prueba 2",
        )
        db.add_all([titular_servicio1, titular_servicio2])

        # --- Importaciones (usuario_id) ------------------------------------
        importacion1 = Importacion(
            usuario_id=usuario_id,
            tipo="Contactos",
            archivo="contactos_prueba.csv",
            registros=100,
            errores=2,
            fecha=ahora,
        )
        db.add(importacion1)

        db.commit()

        # --- Refrescar para tener los ids generados por la BD -------------
        for obj in [
            proveedor1, proveedor2, actividad1, actividad2,
            servicio1, servicio2, embudo1, etapa1, etapa2, etapa3,
            empresa1, empresa2, contacto1, contacto2, contacto3,
            etiqueta1, etiqueta2, campana1, campana2, segmento1, segmento2,
            oportunidad1, oportunidad2, bitacora1, bitacora2,
            titular_servicio1, titular_servicio2, importacion1,
        ]:
            db.refresh(obj)

        log("Insercion completada correctamente. Detalle de registros creados:")
        log("")
        log(f"[mercadeo_crm_proveedores] id={proveedor1.id} nombre={proveedor1.nombre!r}")
        log(f"[mercadeo_crm_proveedores] id={proveedor2.id} nombre={proveedor2.nombre!r}")
        log(f"[mercadeo_crm_actividad]   id={actividad1.id} nombre={actividad1.nombre!r} proveedor_id={actividad1.proveedor_id}")
        log(f"[mercadeo_crm_actividad]   id={actividad2.id} nombre={actividad2.nombre!r} proveedor_id={actividad2.proveedor_id}")
        log(f"[mercadeo_crm_servicios]   id={servicio1.id} nombre={servicio1.nombre!r} responsable_id={servicio1.responsable_id}")
        log(f"[mercadeo_crm_servicios]   id={servicio2.id} nombre={servicio2.nombre!r} responsable_id={servicio2.responsable_id}")
        log(f"[mercadeo_crm_embudos]     id={embudo1.id} nombre={embudo1.nombre!r}")
        log(f"[mercadeo_crm_etapas_embudo] id={etapa1.id} nombre={etapa1.nombre!r} embudo_id={etapa1.embudo_id}")
        log(f"[mercadeo_crm_etapas_embudo] id={etapa2.id} nombre={etapa2.nombre!r} embudo_id={etapa2.embudo_id}")
        log(f"[mercadeo_crm_etapas_embudo] id={etapa3.id} nombre={etapa3.nombre!r} embudo_id={etapa3.embudo_id}")
        log(f"[mercadeo_crm_empresas]    id={empresa1.id} razon_social={empresa1.razon_social!r} responsable_id={empresa1.responsable_id}")
        log(f"[mercadeo_crm_empresas]    id={empresa2.id} razon_social={empresa2.razon_social!r} responsable_id={empresa2.responsable_id}")
        log(f"[mercadeo_crm_contactos]   id={contacto1.id} nombre={contacto1.nombre1} {contacto1.apellido1} empresa_id={contacto1.empresa_id} responsable_id={contacto1.responsable_id}")
        log(f"[mercadeo_crm_contactos]   id={contacto2.id} nombre={contacto2.nombre1} {contacto2.apellido1} empresa_id={contacto2.empresa_id} responsable_id={contacto2.responsable_id}")
        log(f"[mercadeo_crm_contactos]   id={contacto3.id} nombre={contacto3.nombre1} {contacto3.apellido1} empresa_id={contacto3.empresa_id} responsable_id={contacto3.responsable_id}")
        log(f"[mercadeo_crm_etiquetas]   id={etiqueta1.id} nombre={etiqueta1.nombre!r}")
        log(f"[mercadeo_crm_etiquetas]   id={etiqueta2.id} nombre={etiqueta2.nombre!r}")
        log(f"[mercadeo_crm_contacto_etiqueta] contacto_id={contacto_etiqueta1.contacto_id} etiqueta_id={contacto_etiqueta1.etiqueta_id} usuario_id={contacto_etiqueta1.usuario_id}")
        log(f"[mercadeo_crm_contacto_etiqueta] contacto_id={contacto_etiqueta2.contacto_id} etiqueta_id={contacto_etiqueta2.etiqueta_id} usuario_id={contacto_etiqueta2.usuario_id}")
        log(f"[mercadeo_crm_campanas]    id={campana1.id} nombre={campana1.nombre!r}")
        log(f"[mercadeo_crm_campanas]    id={campana2.id} nombre={campana2.nombre!r}")
        log(f"[mercadeo_crm_segmentos]   id={segmento1.id} nombre={segmento1.nombre!r} usuario_id={segmento1.usuario_id}")
        log(f"[mercadeo_crm_segmentos]   id={segmento2.id} nombre={segmento2.nombre!r} usuario_id={segmento2.usuario_id}")
        log(f"[mercadeo_crm_campana_segmento] campana_id={campana_segmento1.campana_id} segmento_id={campana_segmento1.segmento_id} usuario_id={campana_segmento1.usuario_id}")
        log(f"[mercadeo_crm_campana_segmento] campana_id={campana_segmento2.campana_id} segmento_id={campana_segmento2.segmento_id} usuario_id={campana_segmento2.usuario_id}")
        log(f"[mercadeo_crm_oportunidades] id={oportunidad1.id} empresa_id={oportunidad1.empresa_id} contacto_id={oportunidad1.contacto_id} servicio_id={oportunidad1.servicio_id} responsable_id={oportunidad1.responsable_id} plan_liga_titular_id={oportunidad1.plan_liga_titular_id}")
        log(f"[mercadeo_crm_oportunidades] id={oportunidad2.id} empresa_id={oportunidad2.empresa_id} contacto_id={oportunidad2.contacto_id} servicio_id={oportunidad2.servicio_id} responsable_id={oportunidad2.responsable_id} plan_liga_titular_id={oportunidad2.plan_liga_titular_id}")
        log(f"[mercadeo_crm_bitacora]    id={bitacora1.id} tipo={bitacora1.tipo!r} usuario_id={bitacora1.usuario_id} titular_id={bitacora1.titular_id} oportunidad_id={bitacora1.oportunidad_id}")
        log(f"[mercadeo_crm_bitacora]    id={bitacora2.id} tipo={bitacora2.tipo!r} usuario_id={bitacora2.usuario_id} titular_id={bitacora2.titular_id} oportunidad_id={bitacora2.oportunidad_id}")
        log(f"[mercadeo_crm_titular_servicios] id={titular_servicio1.id} planliga_id={titular_servicio1.planliga_id} servicio_id={titular_servicio1.servicio_id}")
        log(f"[mercadeo_crm_titular_servicios] id={titular_servicio2.id} planliga_id={titular_servicio2.planliga_id} servicio_id={titular_servicio2.servicio_id}")
        log(f"[mercadeo_crm_importaciones] id={importacion1.id} archivo={importacion1.archivo!r} usuario_id={importacion1.usuario_id}")

    except Exception:
        db.rollback()
        log("")
        log("ERROR: la insercion fallo y se hizo rollback. Revisa el traceback en consola.")
        raise
    finally:
        db.close()
        LOG_PATH.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        print(f"\nLog escrito en: {LOG_PATH}")


if __name__ == "__main__":
    main()
