from pydantic import BaseModel


class PageLink(BaseModel):
    id: str
    name: str
    url: str
    ip: str
    icon: str = "🔗"
    description: str = ""
