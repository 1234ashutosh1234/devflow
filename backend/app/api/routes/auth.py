from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    data: UserRegister,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    return service.register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: UserLogin,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    access_token, user = service.login(
        email=data.email,
        password=data.password,
    )

    return TokenResponse(
        access_token=access_token,
        user=user,
    )