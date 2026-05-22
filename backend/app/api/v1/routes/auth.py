from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user, require_roles
from backend.app.core.config import get_settings
from backend.app.core.permissions import permissions_for_role
from backend.app.core.rate_limit import login_rate_limiter
from backend.app.core.security import create_access_token
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.auth import (
    BackendRestartAuthorizationRequest,
    BackendRestartAuthorizationResponse,
    BackendRestartNoticePollResponse,
    BackendRestartNoticeResponse,
    BackendRestartPermissionsResponse,
    BackendRestartPermissionsUpdateRequest,
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
from backend.app.services.backend_restart_control import (
    authorize_backend_restart,
    get_backend_restart_allowed_emails,
    get_latest_backend_restart_notice,
    set_backend_restart_allowed_emails,
)
from backend.app.services.password_resets import create_password_reset_request
from backend.app.services.resource_access import get_user_resource_access, get_user_tool_specialties
from backend.app.services.users import authenticate_user, change_user_password

router = APIRouter(prefix="/auth", tags=["auth"])

DatabaseSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
admin_user = require_roles(UserRole.ADMIN)
AdminUser = Annotated[User, Depends(admin_user)]


@router.post("/login", response_model=TokenResponse)
def login(request: Request, payload: LoginRequest, db: DatabaseSession) -> TokenResponse:
    settings = get_settings()
    client_host = request.client.host if request.client else "unknown"
    rate_limit_key = f"login:{client_host}:{payload.email.strip().lower()}"
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
    token_user.resource_access = get_user_resource_access(db, user)
    token_user.tools_specialties = get_user_tool_specialties(db, user)

    return TokenResponse(
        access_token=access_token,
        must_change_password=user.must_change_password,
        user=token_user,
    )


@router.post("/password-reset-requests", response_model=PasswordResetRequestPublicResponse)
def request_password_reset(
    request: Request,
    payload: PasswordResetRequestCreate,
    db: DatabaseSession,
) -> PasswordResetRequestPublicResponse:
    settings = get_settings()
    client_host = request.client.host if request.client else "unknown"
    rate_limit_key = f"password-reset:{client_host}:{payload.email.strip().lower()}"
    if login_rate_limiter.is_limited(
        key=rate_limit_key,
        max_attempts=settings.pro_core_public_rate_limit_attempts,
        window_seconds=settings.pro_core_public_rate_limit_window_seconds,
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Try again later.",
        )
    login_rate_limiter.record_failure(
        key=rate_limit_key,
        window_seconds=settings.pro_core_public_rate_limit_window_seconds,
    )
    create_password_reset_request(db, payload.email)
    return PasswordResetRequestPublicResponse(
        message="Se a conta existir, a solicitacao foi enviada ao responsavel.",
    )


@router.get("/me", response_model=UserProfileResponse)
def me(current_user: CurrentUser, db: DatabaseSession) -> UserProfileResponse:
    profile = UserProfileResponse.model_validate(current_user)
    profile.permissions = permissions_for_role(current_user.role)
    profile.resource_access = get_user_resource_access(db, current_user)
    profile.tools_specialties = get_user_tool_specialties(db, current_user)
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


@router.post(
    "/backend-restart/authorize",
    response_model=BackendRestartAuthorizationResponse,
)
def authorize_backend_restart_operation(
    payload: BackendRestartAuthorizationRequest,
    db: DatabaseSession,
) -> BackendRestartAuthorizationResponse:
    try:
        notice = authorize_backend_restart(
            db=db,
            operator_email=payload.operator_email,
            admin_email=payload.admin_email,
            admin_password=payload.admin_password,
            reason_type=payload.reason_type,
            custom_reason=payload.custom_reason,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc

    return BackendRestartAuthorizationResponse(
        message="Reinicio autorizado e aviso global registrado.",
        notice_id=notice["id"],
        reason=notice["reason"],
        created_at=notice["created_at"],
    )


@router.get(
    "/backend-restart/notice",
    response_model=BackendRestartNoticePollResponse,
)
def poll_backend_restart_notice(
    current_user: CurrentUser,
    db: DatabaseSession,
    last_notice_id: str | None = None,
) -> BackendRestartNoticePollResponse:
    notice = get_latest_backend_restart_notice(db, current_user.company_id)
    if not notice:
        return BackendRestartNoticePollResponse(has_notice=False)
    if last_notice_id and notice["id"] == last_notice_id:
        return BackendRestartNoticePollResponse(has_notice=False)

    return BackendRestartNoticePollResponse(
        has_notice=True,
        notice=BackendRestartNoticeResponse.model_validate(notice),
    )


@router.get(
    "/backend-restart/permissions",
    response_model=BackendRestartPermissionsResponse,
)
def list_backend_restart_permissions(
    current_user: AdminUser,
    db: DatabaseSession,
) -> BackendRestartPermissionsResponse:
    emails = get_backend_restart_allowed_emails(db, current_user.company_id)
    return BackendRestartPermissionsResponse(allowed_emails=emails)


@router.put(
    "/backend-restart/permissions",
    response_model=BackendRestartPermissionsResponse,
)
def update_backend_restart_permissions(
    payload: BackendRestartPermissionsUpdateRequest,
    current_user: AdminUser,
    db: DatabaseSession,
) -> BackendRestartPermissionsResponse:
    emails = set_backend_restart_allowed_emails(db, current_user.company_id, payload.allowed_emails)
    return BackendRestartPermissionsResponse(allowed_emails=emails)
