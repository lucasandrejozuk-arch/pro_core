from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.company import Company
from backend.app.models.configuration import AppSetting, BackupPolicy
from backend.app.schemas.configuration import SystemSettingsUpdate

THEME_SETTING_KEY = "ui.theme"
BRAND_NAME_SETTING_KEY = "ui.brand_name"
BRAND_SUBTITLE_SETTING_KEY = "ui.brand_subtitle"
COLOR_PALETTE_SETTING_KEY = "ui.color_palette"
PRIMARY_COLOR_SETTING_KEY = "ui.primary_color"
LANGUAGE_SETTING_KEY = "ui.language"
DEFAULT_THEME = "light"
DEFAULT_COLOR_PALETTE = "blue"
DEFAULT_LANGUAGE = "pt-BR"
DEFAULT_PRIMARY_COLOR = "#25636f"
DEFAULT_LOGIN_BRAND_NAME = "PRO CORE"
DEFAULT_LOGIN_BRAND_SUBTITLE = "Gestao completa para assistencias tecnicas"
THEME_PRIMARY_COLORS = {
    "light": {
        "blue": "#25636f",
        "green": "#0f766e",
        "amber": "#9a6700",
        "ruby": "#a12f42",
        "cyan": "#087990",
    },
    "dark": {
        "blue": "#38bdf8",
        "green": "#0f766e",
        "amber": "#f2b84b",
        "ruby": "#ff8aa0",
        "cyan": "#22d3ee",
    },
}


def get_system_settings(db: Session, company_id: uuid.UUID) -> dict:
    company = _get_company(db, company_id)
    backup_policy = get_or_create_backup_policy(db, company)
    appearance = get_appearance_settings(db, company_id)

    return {
        "company_id": company.id,
        "company_name": company.name,
        "trade_name": company.trade_name,
        "document_number": company.document_number,
        "email": company.email,
        "phone": company.phone,
        **appearance,
        "backup_enabled": backup_policy.enabled,
        "backup_interval_hours": backup_policy.interval_hours,
        "backup_storage_path": backup_policy.storage_path,
        "backup_last_run_at": backup_policy.last_run_at,
    }


def update_system_settings(
    db: Session,
    company_id: uuid.UUID,
    payload: SystemSettingsUpdate,
) -> dict:
    company = _get_company(db, company_id)
    backup_policy = get_or_create_backup_policy(db, company)
    update_data = payload.model_dump(exclude_unset=True)

    company_fields = {
        "company_name": "name",
        "trade_name": "trade_name",
        "document_number": "document_number",
        "email": "email",
        "phone": "phone",
    }
    for payload_key, model_key in company_fields.items():
        if payload_key in update_data:
            setattr(company, model_key, update_data[payload_key])

    if "backup_enabled" in update_data:
        backup_policy.enabled = update_data["backup_enabled"]
    if "backup_interval_hours" in update_data:
        backup_policy.interval_hours = update_data["backup_interval_hours"]
        company.backup_interval_hours = update_data["backup_interval_hours"]
    if "backup_storage_path" in update_data:
        backup_policy.storage_path = update_data["backup_storage_path"]
    if "theme" in update_data:
        set_setting_value(
            db,
            company_id,
            THEME_SETTING_KEY,
            update_data["theme"],
            "Tema visual padrao da empresa.",
        )
    if "language" in update_data:
        set_setting_value(
            db,
            company_id,
            LANGUAGE_SETTING_KEY,
            update_data["language"] or DEFAULT_LANGUAGE,
            "Idioma padrao da interface.",
        )
    if "brand_name" in update_data:
        set_setting_value(
            db,
            company_id,
            BRAND_NAME_SETTING_KEY,
            update_data["brand_name"] or "",
            "Nome exibido na interface do sistema.",
        )
    if "brand_subtitle" in update_data:
        set_setting_value(
            db,
            company_id,
            BRAND_SUBTITLE_SETTING_KEY,
            update_data["brand_subtitle"] or "",
            "Subtitulo exibido na interface do sistema.",
        )
    if "color_palette" in update_data:
        set_setting_value(
            db,
            company_id,
            COLOR_PALETTE_SETTING_KEY,
            update_data["color_palette"] or DEFAULT_COLOR_PALETTE,
            "Paleta de cores da identidade visual.",
        )
    elif "primary_color" in update_data:
        theme_for_palette = update_data.get("theme") or get_setting_value(
            db,
            company_id,
            THEME_SETTING_KEY,
        )
        if theme_for_palette not in THEME_PRIMARY_COLORS:
            theme_for_palette = DEFAULT_THEME
        set_setting_value(
            db,
            company_id,
            COLOR_PALETTE_SETTING_KEY,
            _palette_from_primary_color(theme_for_palette, update_data["primary_color"]),
            "Paleta de cores da identidade visual.",
        )

    db.add(company)
    db.add(backup_policy)
    db.commit()
    return get_system_settings(db, company_id)


def get_appearance_settings(db: Session, company_id: uuid.UUID) -> dict:
    _get_company(db, company_id)
    theme = get_setting_value(db, company_id, THEME_SETTING_KEY) or DEFAULT_THEME
    if theme not in {"light", "dark"}:
        theme = DEFAULT_THEME

    color_palette = get_setting_value(db, company_id, COLOR_PALETTE_SETTING_KEY)
    if not _is_valid_palette(theme, color_palette):
        color_palette = _legacy_palette(db, company_id, theme)
    primary_color = THEME_PRIMARY_COLORS[theme][color_palette]
    language = get_setting_value(db, company_id, LANGUAGE_SETTING_KEY) or DEFAULT_LANGUAGE
    if language not in {"pt-BR", "en-US"}:
        language = DEFAULT_LANGUAGE

    return {
        "brand_name": get_setting_value(db, company_id, BRAND_NAME_SETTING_KEY) or None,
        "brand_subtitle": get_setting_value(db, company_id, BRAND_SUBTITLE_SETTING_KEY) or None,
        "color_palette": color_palette,
        "primary_color": primary_color,
        "theme": theme,
        "language": language,
    }


def get_login_appearance_settings(db: Session) -> dict:
    statement = (
        select(Company)
        .where(Company.is_active.is_(True))
        .order_by(Company.created_at.asc(), Company.id.asc())
    )
    company = db.scalars(statement).first()
    if company is None:
        return {
            "brand_name": DEFAULT_LOGIN_BRAND_NAME,
            "brand_subtitle": DEFAULT_LOGIN_BRAND_SUBTITLE,
            "color_palette": DEFAULT_COLOR_PALETTE,
            "primary_color": DEFAULT_PRIMARY_COLOR,
            "theme": DEFAULT_THEME,
            "language": DEFAULT_LANGUAGE,
        }

    appearance = get_appearance_settings(db, company.id)
    return {
        **appearance,
        "brand_name": appearance["brand_name"] or DEFAULT_LOGIN_BRAND_NAME,
        "brand_subtitle": appearance["brand_subtitle"] or DEFAULT_LOGIN_BRAND_SUBTITLE,
    }


def get_or_create_backup_policy(db: Session, company: Company) -> BackupPolicy:
    statement = select(BackupPolicy).where(BackupPolicy.company_id == company.id)
    backup_policy = db.scalars(statement).first()
    if backup_policy is not None:
        return backup_policy

    backup_policy = BackupPolicy(
        company_id=company.id,
        enabled=True,
        interval_hours=company.backup_interval_hours,
        storage_path="backups",
    )
    db.add(backup_policy)
    db.commit()
    db.refresh(backup_policy)
    return backup_policy


def get_setting_value(db: Session, company_id: uuid.UUID, key: str) -> str | None:
    statement = select(AppSetting).where(
        AppSetting.company_id == company_id,
        AppSetting.key == key,
    )
    setting = db.scalars(statement).first()
    return setting.value if setting else None


def set_setting_value(
    db: Session,
    company_id: uuid.UUID,
    key: str,
    value: str,
    description: str | None = None,
) -> AppSetting:
    statement = select(AppSetting).where(
        AppSetting.company_id == company_id,
        AppSetting.key == key,
    )
    setting = db.scalars(statement).first()
    if setting is None:
        setting = AppSetting(
            company_id=company_id,
            key=key,
            value=value,
            description=description,
        )
    else:
        setting.value = value
        setting.description = description

    db.add(setting)
    return setting


def _get_company(db: Session, company_id: uuid.UUID) -> Company:
    company = db.get(Company, company_id)
    if company is None:
        raise ValueError("Company not found.")
    return company


def _is_hex_color(value: str) -> bool:
    if len(value) != 7 or not value.startswith("#"):
        return False
    return all(character in "0123456789abcdefABCDEF" for character in value[1:])


def _is_valid_palette(theme: str, color_palette: str | None) -> bool:
    return bool(color_palette and color_palette in THEME_PRIMARY_COLORS[theme])


def _legacy_palette(db: Session, company_id: uuid.UUID, theme: str) -> str:
    primary_color = get_setting_value(db, company_id, PRIMARY_COLOR_SETTING_KEY)
    if not primary_color or not _is_hex_color(primary_color):
        return DEFAULT_COLOR_PALETTE
    return _palette_from_primary_color(theme, primary_color)


def _palette_from_primary_color(theme: str, primary_color: str | None) -> str:
    if not primary_color or not _is_hex_color(primary_color):
        return DEFAULT_COLOR_PALETTE

    target = _hex_to_rgb(primary_color)
    distances = {
        palette_id: sum(
            (target_channel - palette_channel) ** 2
            for target_channel, palette_channel in zip(
                target,
                _hex_to_rgb(color),
                strict=True,
            )
        )
        for palette_id, color in THEME_PRIMARY_COLORS[theme].items()
    }
    return min(distances, key=distances.get)


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    return int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16)
