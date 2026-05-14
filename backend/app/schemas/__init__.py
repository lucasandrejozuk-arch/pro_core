"""Request and response schemas."""

from backend.app.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    TokenResponse,
    TokenUser,
    UserProfileResponse,
)
from backend.app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from backend.app.schemas.equipment import EquipmentCreate, EquipmentResponse, EquipmentUpdate
from backend.app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
)
from backend.app.schemas.service_order import (
    BudgetItemCreate,
    BudgetItemResponse,
    DiagnosisRequest,
    RejectServiceOrderRequest,
    ServiceOrderCreate,
    ServiceOrderResponse,
    ServiceOrderUpdate,
)
from backend.app.schemas.user import UserSummaryResponse

__all__ = [
    "BudgetItemCreate",
    "BudgetItemResponse",
    "CustomerCreate",
    "CustomerResponse",
    "CustomerUpdate",
    "DiagnosisRequest",
    "EquipmentCreate",
    "EquipmentResponse",
    "EquipmentUpdate",
    "InventoryItemCreate",
    "InventoryItemResponse",
    "InventoryItemUpdate",
    "LoginRequest",
    "PasswordChangeRequest",
    "RejectServiceOrderRequest",
    "ServiceOrderCreate",
    "ServiceOrderResponse",
    "ServiceOrderUpdate",
    "TokenResponse",
    "TokenUser",
    "UserProfileResponse",
    "UserSummaryResponse",
]
