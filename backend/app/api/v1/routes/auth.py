from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.core.config import get_settings
from backend.app.core.permissions import permissions_for_role
from backend.app.core.rate_limit import login_rate_limiter
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
from backend.app.schemas.password_reset import (
    PasswordResetRequestCreate,
    PasswordResetRequestPublicResponse,
)
from backend.app.services.password_resets import create_password_reset_request
from backend.app.services.users import authenticate_user, change_user_password

router = APIRouter(prefix="/auth", tags=["auth"])

DatabaseSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/login", response_model=TokenResponse)
def login(request: Request, payload: LoginRequest, db: DatabaseSession) -> TokenResponse:
    settings = get_settings()
    client_host = request.client.host if request.client else "unknown"
    rate_limit_key = f"{client_host}:{payload.email}"
    if login_rate_limiter.is_limited(
        key=rate_limit_key,
        max_attempts=settings.pro_core_login_rate_limit_attempts,
        window_seconds=settings.pro_core_login_rate_limit_window_seconds,
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )

    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        login_rate_limiter.record_failure(
            key=rate_limit_key,
            window_seconds=settings.pro_core_login_rate_limit_window_seconds,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    login_rate_limiter.clear(rate_limit_key)

    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={
            "company_id": str(user.company_id),
            "role": user.role.value,
        },
    )

    token_user = TokenUser.model_validate(user)
    token_user.permissions = permissions_for_role(user.role)

    return TokenResponse(
        access_token=access_token,
        must_change_password=user.must_change_password,
        user=token_user,
    )


@router.post("/password-reset-requests", response_model=PasswordResetRequestPublicResponse)
def request_password_reset(
    payload: PasswordResetRequestCreate,
    db: DatabaseSession,
) -> PasswordResetRequestPublicResponse:
    create_password_reset_request(db, payload.email)
    return PasswordResetRequestPublicResponse(
        message="Se a conta existir, a solicitacao foi enviada ao responsavel.",
    )


@router.get("/me", response_model=UserProfileResponse)
def me(current_user: CurrentUser) -> UserProfileResponse:
    profile = UserProfileResponse.model_validate(current_user)
    profile.permissions = permissions_for_role(current_user.role)
    return profile


@router.post("/change-password", response_model=UserProfileResponse)
def change_password(
    payload: PasswordChangeRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
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
