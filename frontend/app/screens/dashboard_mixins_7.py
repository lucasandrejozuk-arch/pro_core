from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QLineEdit,
)

from frontend.app.themes.styles import COLOR_PALETTE_OPTIONS, DEFAULT_COLOR_PALETTE


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardMixin7:
    def _format_inventory_full_summary(self, item: dict[str, Any]) -> str:
        quantity = self._format_value(item.get("quantity")) or "0"
        minimum = self._format_value(item.get("minimum_quantity")) or "0"
        unit_cost = self._format_value(item.get("unit_cost")) or "0"
        status = "Critico" if self._inventory_is_low(item) else "Operacional"
        lines = [
            f"SKU: {self._format_value(item.get('sku')) or '-'}",
            f"Nome: {self._format_value(item.get('name')) or '-'}",
            f"Categoria: {self._format_value(item.get('category')) or '-'}",
            f"Quantidade: {quantity}",
            f"Minimo para reposicao: {minimum}",
            f"Custo unitario: {unit_cost}",
            f"Status: {status}",
        ]
        return "\n".join(lines)

    def _format_settings_summary(self, settings: dict[str, Any]) -> str:
        backup_enabled = "Ativo" if settings.get("backup_enabled", True) else "Inativo"
        theme = self._format_value(settings.get("theme")) or str(settings.get("theme") or "light")
        color_palette = self._format_color_palette(settings.get("color_palette"))
        language = self._format_language(settings.get("language"))
        lines = [
            f"Empresa: {self._format_value(settings.get('company_name')) or '-'}",
            f"Nome fantasia: {self._format_value(settings.get('trade_name')) or '-'}",
            f"Nome exibido: {self._format_value(settings.get('brand_name')) or '-'}",
            f"Subtitulo: {self._format_value(settings.get('brand_subtitle')) or '-'}",
            f"Paleta: {color_palette}",
            f"Tema: {theme}",
            f"Idioma: {language}",
            f"Escala da interface: {round(self.ui_scale_value * 100)}%",
            f"Backup automatico: {backup_enabled}",
            f"Intervalo de backup: {settings.get('backup_interval_hours') or 24} hora(s)",
            f"Destino: {self._format_value(settings.get('backup_storage_path')) or 'backups'}",
            f"Ultimo backup: {self._format_value(settings.get('backup_last_run_at')) or 'nunca'}",
        ]
        return "\n".join(lines)

    def _format_audit_summary(self, record: dict[str, Any]) -> str:
        actor = self._format_value(record.get("actor_user_id")) or record.get("actor_type") or "-"
        lines = [
            f"Acao: {self._format_value(record.get('action')) or '-'}",
            f"Entidade: {self._format_value(record.get('entity_type')) or '-'}",
            f"ID: {self._format_value(record.get('entity_id')) or '-'}",
            f"Resumo: {self._format_value(record.get('summary')) or '-'}",
            f"Ator: {actor}",
            f"Criado em: {self._format_value(record.get('created_at')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_sector_summary(self, sector: dict[str, Any]) -> str:
        lines = [
            f"Nome: {self._format_value(sector.get('name')) or '-'}",
            f"Descricao: {self._format_value(sector.get('description')) or '-'}",
            f"Criado em: {self._format_value(sector.get('created_at')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_user_summary(self, user: dict[str, Any]) -> str:
        sector_name = self._lookup_label(
            self.user_sectors,
            user.get("sector_id"),
            "name",
            "Sem setor",
        )
        active = "Ativo" if user.get("is_active", True) else "Inativo"
        must_change = "Sim" if user.get("must_change_password", False) else "Nao"
        lines = [
            f"Nome: {self._format_value(user.get('full_name')) or '-'}",
            f"Email: {self._format_value(user.get('email')) or '-'}",
            f"Perfil: {self._format_value(user.get('role')) or '-'}",
            f"Setor: {sector_name}",
            f"Status: {active}",
            f"Exige troca de senha: {must_change}",
        ]
        return "\n".join(lines)

    def _format_password_reset_summary(self, request: dict[str, Any]) -> str:
        lines = [
            f"Solicitante: {self._format_value(request.get('requester_full_name')) or '-'}",
            f"Email: {self._format_value(request.get('requester_email')) or '-'}",
            f"Perfil: {self._format_value(request.get('requester_role')) or '-'}",
            f"Status: {self._format_value(request.get('status')) or '-'}",
            f"Criada em: {self._format_value(request.get('created_at')) or '-'}",
        ]
        return "\n".join(lines)

    def _inventory_is_low(self, item: dict[str, Any]) -> bool:
        quantity = self._safe_float(item.get("quantity"))
        minimum = self._safe_float(item.get("minimum_quantity"))
        return minimum > 0 and quantity <= minimum

    @staticmethod
    def _safe_float(value: Any) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    def _lookup_label(
        self,
        items: list[dict[str, Any]],
        item_id: Any,
        key: str,
        fallback: str,
    ) -> str:
        for item in items:
            if str(item.get("id")) == str(item_id):
                return str(item.get(key) or fallback)
        return fallback

    def _lookup_equipment_label(self, equipment_id: Any) -> str:
        for equipment in self.service_order_equipment:
            if str(equipment.get("id")) != str(equipment_id):
                continue
            parts = [
                str(equipment.get("category") or ""),
                str(equipment.get("brand") or ""),
                str(equipment.get("model") or ""),
                str(equipment.get("special_number") or ""),
                str(equipment.get("serial_number") or ""),
            ]
            return " - ".join(part for part in parts if part) or "Equipamento sem descricao"
        return "Equipamento nao identificado"

    @staticmethod
    def _optional_text(input_widget: QLineEdit) -> str | None:
        value = input_widget.text().strip()
        return value or None

    @staticmethod
    def _is_complete_phone(value: str) -> bool:
        digits = "".join(character for character in value if character.isdigit())
        return "_" not in value and len(digits) == 11

    @staticmethod
    def _populate_color_palette_combo(combo: QComboBox) -> None:
        combo.clear()
        for palette_id, label in COLOR_PALETTE_OPTIONS:
            combo.addItem(label, palette_id)

    @staticmethod
    def _format_color_palette(value: object) -> str:
        value_text = str(value or DEFAULT_COLOR_PALETTE)
        for palette_id, label in COLOR_PALETTE_OPTIONS:
            if palette_id == value_text:
                return label
        return COLOR_PALETTE_OPTIONS[0][1]

    @staticmethod
    def _format_language(value: object) -> str:
        languages = {
            "pt-BR": "Portugues brasileiro",
            "en-US": "English (US)",
        }
        return languages.get(str(value or "pt-BR"), "Portugues brasileiro")

    @staticmethod
    def _select_combo_value(combo: QComboBox, value: str) -> None:
        for index in range(combo.count()):
            if str(combo.itemData(index)) == value:
                combo.setCurrentIndex(index)
                return

    def _decimal_text(self, input_widget: QLineEdit, label: str) -> str | None:
        value = input_widget.text().strip().replace(",", ".")
        if not value:
            value = "0"

        try:
            numeric_value = float(value)
        except ValueError:
            self.set_inventory_form_status(f"{label} deve ser numerico.", is_error=True)
            return None

        if numeric_value < 0:
            self.set_inventory_form_status(f"{label} nao pode ser negativo.", is_error=True)
            return None

        return value

    def _decimal_text_for_service_order(
        self,
        input_widget: QLineEdit,
        label: str,
        allow_zero: bool,
    ) -> str | None:
        value = input_widget.text().strip().replace(",", ".")
        if not value:
            value = "0"

        try:
            numeric_value = float(value)
        except ValueError:
            self.set_service_order_form_status(f"{label} deve ser numerico.", is_error=True)
            return None

        if numeric_value < 0 or (numeric_value == 0 and not allow_zero):
            self.set_service_order_form_status(f"{label} deve ser maior que zero.", is_error=True)
            return None

        return value
