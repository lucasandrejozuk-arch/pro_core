from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QLineEdit,
)

from frontend.app.core.inventory_catalog import STOCK_GROUP_OPTIONS
from frontend.app.themes.styles import COLOR_PALETTE_OPTIONS, DEFAULT_COLOR_PALETTE


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardMixin7:
    def _format_inventory_full_summary(self, item: dict[str, Any]) -> str:
        quantity = self._format_value(item.get("quantity")) or "0"
        minimum = self._format_value(item.get("minimum_quantity")) or "0"
        unit_cost = self._format_value(item.get("unit_cost")) or "0"
        quantity_value = self._safe_float(item.get("quantity"))
        minimum_value = self._safe_float(item.get("minimum_quantity"))
        unit_cost_value = self._safe_float(item.get("unit_cost"))
        reorder_quantity = max(0.0, minimum_value - quantity_value)
        stock_value = max(0.0, quantity_value * unit_cost_value)
        status = "Critico" if self._inventory_is_low(item) else "Operacional"
        stock_group = self._format_inventory_stock_group(item.get("stock_group"))
        technical_data = (
            item.get("technical_data") if isinstance(item.get("technical_data"), dict) else {}
        )
        technical_lines = [
            f"- {key.replace('_', ' ').title()}: {self._format_value(value) or '-'}"
            for key, value in technical_data.items()
            if self._format_value(value)
        ]
        lines = [
            f"Submodulo: {stock_group}",
            f"SKU: {self._format_value(item.get('sku')) or '-'}",
            f"Nome: {self._format_value(item.get('name')) or '-'}",
            f"Categoria: {self._format_value(item.get('category')) or '-'}",
            f"Localizacao: {self._format_value(item.get('location')) or '-'}",
            f"Quantidade: {quantity}",
            f"Minimo para reposicao: {minimum}",
            f"Custo unitario: {unit_cost}",
            f"Reposicao necessaria: {self._format_number(reorder_quantity)}",
            f"Valor em estoque: R$ {self._format_number(stock_value)}",
            f"Status: {status}",
            f"Observacoes: {self._format_value(item.get('notes')) or '-'}",
        ]
        if technical_lines:
            lines.append("Especificacoes tecnicas:")
            lines.extend(technical_lines)
        document_lines = self._format_inventory_documents(item.get("documents"))
        if document_lines:
            lines.append("Anexos:")
            lines.extend(document_lines)
        return "\n".join(lines)

    @staticmethod
    def _format_inventory_stock_group(value: Any) -> str:
        stock_group = str(value or "components")
        for key, label in STOCK_GROUP_OPTIONS:
            if key == stock_group:
                return label
        return stock_group

    def _format_inventory_documents(self, documents: Any) -> list[str]:
        if not isinstance(documents, list):
            return []
        lines: list[str] = []
        for document in documents[:5]:
            if not isinstance(document, dict):
                continue
            file_name = self._format_value(document.get("file_name")) or "arquivo"
            document_type = self._format_value(document.get("document_type")) or "outro"
            lines.append(f"- {file_name} ({document_type})")
        remaining = len(documents) - len(lines)
        if remaining > 0:
            lines.append(f"- +{remaining} arquivo(s)")
        return lines

    def _format_audit_summary(self, record: dict[str, Any]) -> str:
        actor = (
            self._format_value(record.get("actor_user_id"))
            or self._format_value(record.get("actor_type"))
            or "-"
        )
        sensitivity = (
            "Sim" if self._audit_action_is_sensitive(str(record.get("action") or "")) else "Nao"
        )
        lines = [
            f"Acao: {self._format_value(record.get('action')) or '-'}",
            f"Entidade: {self._format_value(record.get('entity_type')) or '-'}",
            f"ID: {self._format_value(record.get('entity_id')) or '-'}",
            f"Resumo: {self._format_value(record.get('summary')) or '-'}",
            f"Ator: {actor}",
            f"Evento sensivel: {sensitivity}",
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
        status = self._password_reset_status_label(request.get("status"))
        lines = [
            f"Solicitante: {self._format_value(request.get('requester_full_name')) or '-'}",
            f"Email: {self._format_value(request.get('requester_email')) or '-'}",
            f"Perfil: {self._format_value(request.get('requester_role')) or '-'}",
            f"Status: {status}",
            f"Criada em: {self._format_value(request.get('created_at')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_resource_access_summary(self, record: dict[str, Any]) -> str:
        allowed_resources = record.get("allowed_resources")
        default_resources = record.get("default_resources")
        allowed = (
            ", ".join(str(item) for item in allowed_resources)
            if isinstance(allowed_resources, list) and allowed_resources
            else "Nenhum"
        )
        defaults = (
            ", ".join(str(item) for item in default_resources)
            if isinstance(default_resources, list) and default_resources
            else "Nenhum"
        )
        lines = [
            f"Nome: {self._format_value(record.get('full_name')) or '-'}",
            f"Email: {self._format_value(record.get('email')) or '-'}",
            f"Perfil: {self._format_value(record.get('role')) or '-'}",
            f"Setor: {self._format_value(record.get('sector_name')) or 'Sem setor'}",
            f"Recursos liberados: {allowed}",
            f"Recursos padrao do perfil: {defaults}",
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
    def _is_valid_email(value: str) -> bool:
        email = value.strip()
        if not email or len(email) > 254 or any(character.isspace() for character in email):
            return False
        if email.count("@") != 1:
            return False
        local, domain = email.split("@", 1)
        if not local or not domain or "." not in domain:
            return False
        return not any(part == "" for part in domain.split("."))

    @staticmethod
    def _is_valid_password(value: str) -> bool:
        return len(value) >= 8

    @staticmethod
    def _is_valid_temporary_password(value: str) -> bool:
        return (
            len(value) == 6
            and value.isalnum()
            and any(character.islower() for character in value)
            and any(character.isupper() for character in value)
            and any(character.isdigit() for character in value)
        )

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
