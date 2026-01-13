from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from starlette import status

from ..schemas.auth import LoginResponse, LoginRequest
from ...auth import get_current_admin, create_access_token, authenticate_admin
from ...config import settings


router = APIRouter(prefix="/auth", tags=["auth"])

security = HTTPBearer()

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):

    if not authenticate_admin(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        data={"sub": credentials.username},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": credentials.username
    }


@router.get("/verify")
async def verify_auth(current_admin: dict = Depends(get_current_admin)):
    return {
        "authenticated": True,
        "username": current_admin.get("sub")
    }


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}