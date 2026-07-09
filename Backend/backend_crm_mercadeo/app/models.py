from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Etiqueta(Base):
    __tablename__ = "mercadeo_crm_etiquetas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(20))

    contactos: Mapped[list["ContactoEtiqueta"]] = relationship(back_populates="etiqueta")


class ContactoEtiqueta(Base):
    __tablename__ = "mercadeo_crm_contacto_etiqueta"

    contacto_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    etiqueta_id: Mapped[int] = mapped_column(
        ForeignKey("mercadeo_crm_etiquetas.id"), primary_key=True
    )
    usuario_id: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[datetime] = mapped_column(DateTime)

    etiqueta: Mapped["Etiqueta"] = relationship(back_populates="contactos")


class Campana(Base):
    __tablename__ = "mercadeo_crm_campanas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    asunto: Mapped[str] = mapped_column(String(200))
    contenido: Mapped[str] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(30))
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date] = mapped_column(Date)

    segmentos: Mapped[list["CampanaSegmento"]] = relationship(back_populates="campana")


class Segmento(Base):
    __tablename__ = "mercadeo_crm_segmentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    filtros: Mapped[str] = mapped_column(Text)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime)
    usuario_id: Mapped[int] = mapped_column(Integer)

    campanas: Mapped[list["CampanaSegmento"]] = relationship(back_populates="segmento")


class CampanaSegmento(Base):
    __tablename__ = "mercadeo_crm_campana_segmento"

    campana_id: Mapped[int] = mapped_column(
        ForeignKey("mercadeo_crm_campanas.id"), primary_key=True
    )
    segmento_id: Mapped[int] = mapped_column(
        ForeignKey("mercadeo_crm_segmentos.id"), primary_key=True
    )
    usuario_id: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[datetime] = mapped_column(DateTime)

    campana: Mapped["Campana"] = relationship(back_populates="segmentos")
    segmento: Mapped["Segmento"] = relationship(back_populates="campanas")
