from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.core.security import create_access_token
from app.dependencies import get_current_user
from app.schemas.auth import AuthResponse, LoginRequest, UserInfo
from app.services.sso_service import clear_credentials, store_credentials
from app.services.users_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
async def login(form: LoginRequest):
    try:
        user = authenticate_user(form.username, form.password)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar con la base de datos",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    store_credentials(
        user["username"],
        form.password,
        user.get("sso_username", user["username"]),
    )

    token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return AuthResponse(
        token=token,
        role=user.get("portal_role", user["role"]),
        username=user["username"],
        nombres=user.get("nombres", user["username"]),
        portal_role=user.get("portal_role", user["role"]),
        id_area=user.get("id_area"),
        area_name=user.get("area_name", ""),
    )


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserInfo(
        username=current_user["username"],
        nombres=current_user.get("nombres", current_user["username"]),
        role=current_user.get("role", "usuario"),
        portal_role=current_user.get("portal_role", current_user.get("role", "usuario")),
        id_area=current_user.get("id_area"),
        area_name=current_user.get("area_name", ""),
        email=current_user.get("email", ""),
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    clear_credentials(current_user["username"])
    return {"ok": True}
