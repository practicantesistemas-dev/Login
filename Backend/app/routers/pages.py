from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.pages import PageLink
from app.services.links_service import get_pages_for_user

router = APIRouter(prefix="/pages", tags=["pages"])


@router.get("", response_model=list[PageLink])
async def list_pages(current_user: dict = Depends(get_current_user)):
    return get_pages_for_user(current_user["username"], current_user["role"])
