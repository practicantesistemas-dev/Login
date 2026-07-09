from typing import Literal

from pydantic import BaseModel, Field


class DepartmentItem(BaseModel):
    id: int
    name: str


class ApplicationItem(BaseModel):
    id: int
    name: str
    url: str = ""
    estado: str = "inactiva"
    linked_count: int = 1


class ApplicationEstadoRequest(BaseModel):
    url: str = Field(min_length=4)
    estado: Literal["activa", "inactiva"]


class ApplicationEstadoResponse(BaseModel):
    url: str
    name: str
    estado: str
    updated_count: int


class ManagedUser(BaseModel):
    id_usuario: int | None = None
    username: str
    nombres: str
    num_id: str
    id_area: int | None = None
    area_name: str = ""
    email_personal: str = ""
    email_laboral: str = ""
    portal_role: str = "usuario"
    report_tipo: str = "user"
    active: bool = True
    app_ids: list[int] = Field(default_factory=list)


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=4, max_length=20)
    nombres: str = Field(min_length=2, max_length=200)
    num_id: str = Field(min_length=1, max_length=20)
    id_area: int
    report_tipo: str = Field(default="user", min_length=1, max_length=10)
    email_personal: str = ""
    email_laboral: str = ""
    portal_role: str = "usuario"
    app_ids: list[int] = Field(default_factory=list)


class UserUpdateRequest(BaseModel):
    password: str | None = Field(default=None, min_length=4, max_length=20)
    nombres: str | None = None
    num_id: str | None = None
    id_area: int | None = None
    report_tipo: str | None = Field(default=None, min_length=1, max_length=10)
    email_personal: str | None = None
    email_laboral: str | None = None
    portal_role: str | None = None
    active: bool | None = None
    app_ids: list[int] | None = None
