from __future__ import annotations

REQUIRED_TECHNICAL_FIELDS_BY_CATEGORY: dict[str, tuple[str, ...]] = {
    "Transformadores": (
        "primary_voltage",
        "secondary_voltage",
        "power",
    )
}


def validate_inventory_category_requirements(
    category: str | None,
    technical_data: dict[str, str] | None,
) -> None:
    category_key = str(category or "").strip()
    required_fields = REQUIRED_TECHNICAL_FIELDS_BY_CATEGORY.get(category_key, ())
    if not required_fields:
        return
    source = technical_data or {}
    missing = [key for key in required_fields if not str(source.get(key) or "").strip()]
    if missing:
        raise ValueError(
            "Missing required technical_data for category " f"{category_key}: {', '.join(missing)}"
        )
