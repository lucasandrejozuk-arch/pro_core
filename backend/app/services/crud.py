from __future__ import annotations

from pydantic import BaseModel


def apply_updates(instance: object, payload: BaseModel) -> None:
    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(instance, field_name, value)

