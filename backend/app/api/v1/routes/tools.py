from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.api.dependencies import require_roles
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.tools import ToolDefinition
from backend.app.services.tools import list_available_tools

router = APIRouter(prefix="/tools", tags=["tools"])
staff_user = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.TECHNICIAN)
StaffUser = Annotated[User, Depends(staff_user)]


@router.get("", response_model=list[ToolDefinition])
def list_tools(current_user: StaffUser) -> list[ToolDefinition]:
    return list_available_tools(current_user)
