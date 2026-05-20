from __future__ import annotations

from pydantic import BaseModel


class ToolDefinition(BaseModel):
    id: str
    name: str
    category: str
    module: str
    description: str
    order: int
