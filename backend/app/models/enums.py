from enum import Enum
from typing import TypeVar

EnumType = TypeVar("EnumType", bound=Enum)


def enum_values(enum_type: type[EnumType]) -> list[str]:
    return [item.value for item in enum_type]


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    TECHNICIAN = "technician"
    CUSTOMER = "customer"


class ServiceOrderStatus(str, Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    PENDING_QUOTE = "pending_quote"
    QUOTE_SENT = "quote_sent"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CLOSED = "closed"


class ServiceOrderPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ServiceOrderEventSource(str, Enum):
    STAFF = "staff"
    CUSTOMER = "customer"
    SYSTEM = "system"


class BudgetItemType(str, Enum):
    SERVICE = "service"
    PART = "part"
    OTHER = "other"


class FinancialRecordType(str, Enum):
    RECEIVABLE = "receivable"
    PAYABLE = "payable"


class FinancialRecordStatus(str, Enum):
    OPEN = "open"
    PAID = "paid"
    CANCELED = "canceled"
    OVERDUE = "overdue"


class NotificationChannel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    SYSTEM = "system"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class DocumentType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    PDF = "pdf"
    INVOICE = "invoice"
    OTHER = "other"
