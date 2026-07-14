from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=500)


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
