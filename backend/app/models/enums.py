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


class BudgetItemType(str, Enum):
    SERVICE = "service"
    PART = "part"
    OTHER = "other"


class DocumentType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    PDF = "pdf"
    INVOICE = "invoice"
    OTHER = "other"
