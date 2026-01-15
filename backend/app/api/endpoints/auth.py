from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm
from starlette import status

from ...core.auth import get_current_admin, create_access_token, verify_password
from ...core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

security = HTTPBearer()


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == settings.ADMIN_USERNAME:
        if verify_password(form_data.password, settings.ADMIN_PASSWORD):
            token = create_access_token(data={"sub": form_data.username})
            return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )



@router.get("/verify")
async def verify_auth(current_admin: dict = Depends(get_current_admin)):
    return {"authenticated": True, "username": current_admin.get("sub")}


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
