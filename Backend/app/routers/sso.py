from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.dependencies import get_current_user
from app.services.sso_service import build_launch_html, resolve_sso_credentials

router = APIRouter(prefix="/sso", tags=["sso"])


class SsoLaunchRequest(BaseModel):
    url: str


def _launch(url: str, current_user: dict) -> HTMLResponse:
    resolved = resolve_sso_credentials(current_user["username"])
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No hay credenciales disponibles para abrir la aplicación. Vuelva a iniciar sesión.",
        )

    app_username, password = resolved
    try:
        html = build_launch_html(url, app_username, password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La URL de la aplicación no es válida.",
        )

    return HTMLResponse(content=html)


@router.post("/launch", response_class=HTMLResponse)
async def launch_app_post(
    body: SsoLaunchRequest,
    current_user: dict = Depends(get_current_user),
):
    return _launch(body.url, current_user)


@router.get("/launch", response_class=HTMLResponse)
async def launch_app_get(
    url: str = Query(..., min_length=8),
    current_user: dict = Depends(get_current_user),
):
    return _launch(url, current_user)
