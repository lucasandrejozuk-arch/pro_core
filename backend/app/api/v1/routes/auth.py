from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.core.security import create_access_token
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    TokenResponse,
    TokenUser,
    UserProfileResponse,
)
from backend.app.services.users import authenticate_user, change_user_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={
            "company_id": str(user.company_id),
            "role": user.role.value,
        },
    )

    return TokenResponse(
        access_token=access_token,
        must_change_password=user.must_change_password,
        user=TokenUser.model_validate(user),
    )


@router.get("/me", response_model=UserProfileResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/change-password", response_model=UserProfileResponse)
def change_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    try:
        return change_user_password(
            db=db,
            user=current_user,
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

