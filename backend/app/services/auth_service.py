from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserRegister


class AuthService:

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def register(self, data: UserRegister):

        existing_email = self.repository.get_by_email(
            data.email
        )

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        existing_username = self.repository.get_by_username(
            data.username
        )

        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        hashed_password = hash_password(
            data.password
        )

        return self.repository.create(
            email=data.email,
            username=data.username,
            hashed_password=hashed_password,
        )

    def login(
        self,
        email: str,
        password: str,
    ):

        user = self.repository.get_by_email(email)

        if not user or not verify_password(
            password,
            user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        access_token = create_access_token(
            subject=str(user.id)
        )

        return access_token, user