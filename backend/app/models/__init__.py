"""Database models."""

from backend.app.models.audit import AuditLog
from backend.app.models.company import Company
from backend.app.models.configuration import AppSetting, BackupPolicy
from backend.app.models.customer import Customer
from backend.app.models.document import DocumentAttachment
from backend.app.models.enums import (
    BudgetItemType,
    DocumentType,
    FinancialRecordStatus,
    FinancialRecordType,
    NotificationChannel,
    NotificationStatus,
    ServiceOrderEventSource,
    ServiceOrderPriority,
    ServiceOrderStatus,
    UserRole,
)
from backend.app.models.equipment import (
    Equipment,
    EquipmentBoard,
    EquipmentBoardComponent,
    EquipmentDefectCase,
)
from backend.app.models.financial import FinancialRecord
from backend.app.models.inventory import InventoryItem
from backend.app.models.notification import NotificationLog
from backend.app.models.password_reset import PasswordResetRequest
from backend.app.models.sector import Sector
from backend.app.models.service_order import (
    ServiceOrder,
    ServiceOrderBudgetItem,
    ServiceOrderEvent,
)
from backend.app.models.user import User

__all__ = [
    "AuditLog",
    "AppSetting",
    "BackupPolicy",
    "BudgetItemType",
    "Company",
    "Customer",
    "DocumentAttachment",
    "DocumentType",
    "Equipment",
    "EquipmentBoard",
    "EquipmentBoardComponent",
    "EquipmentDefectCase",
    "FinancialRecord",
    "FinancialRecordStatus",
    "FinancialRecordType",
    "InventoryItem",
    "NotificationChannel",
    "NotificationLog",
    "NotificationStatus",
    "PasswordResetRequest",
    "Sector",
    "ServiceOrder",
    "ServiceOrderBudgetItem",
    "ServiceOrderEvent",
    "ServiceOrderEventSource",
    "ServiceOrderPriority",
    "ServiceOrderStatus",
    "User",
    "UserRole",
]
