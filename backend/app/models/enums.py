from enum import StrEnum


def enum_values[T: StrEnum](enum_type: type[T]) -> list[str]:
    return [item.value for item in enum_type]


class UserRole(StrEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    TECHNICIAN = "technician"
    CUSTOMER = "customer"


class ServiceOrderStatus(StrEnum):
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


class ServiceOrderPriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ServiceOrderEventSource(StrEnum):
    STAFF = "staff"
    CUSTOMER = "customer"
    SYSTEM = "system"


class BudgetItemType(StrEnum):
    SERVICE = "service"
    PART = "part"
    OTHER = "other"


class DocumentType(StrEnum):
    IMAGE = "image"
    VIDEO = "video"
    PDF = "pdf"
    INVOICE = "invoice"
    OTHER = "other"
