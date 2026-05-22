from __future__ import annotations

from typing import Any


class DashboardEquipmentFieldsMixin:
    @staticmethod
    def _equipment_dialog_fields() -> list[dict[str, Any]]:
        return [
            {
                "key": "category",
                "label": "Tipo:",
                "placeholder": "Tipo do equipamento",
                "required": True,
            },
            {"key": "brand", "label": "Marca:", "placeholder": "Marca do equipamento"},
            {"key": "model", "label": "Modelo:", "placeholder": "Modelo do equipamento"},
            {
                "key": "special_number",
                "label": "No Especial:",
                "placeholder": "Ex.: A5E02814482, S120-CU320",
            },
            {
                "key": "unit_price",
                "label": "Valor Unitario (R$):",
                "placeholder": "Ex.: 1499,90",
                "money": True,
            },
            {
                "key": "description",
                "label": "Notas:",
                "placeholder": "Observacoes gerais (opcional)",
                "multiline": True,
            },
        ]

    @staticmethod
    def _board_dialog_fields() -> list[dict[str, Any]]:
        return [
            {
                "key": "name",
                "label": "Nome:",
                "placeholder": "Nome do objeto vinculado",
                "required": True,
            },
            {
                "key": "special_number",
                "label": "No Especial:",
                "placeholder": "Ex.: A5E02814482, numero de inventario",
            },
            {"key": "model", "label": "Modelo / Tipo:", "placeholder": "Modelo / tipo da placa"},
            {"key": "revision", "label": "Revisao:", "placeholder": "Ex.: A01, B02, Rev.C"},
            {
                "key": "unit_price",
                "label": "Valor Unitario (R$):",
                "placeholder": "Ex.: 980,00",
                "money": True,
            },
            {
                "key": "notes",
                "label": "Notas:",
                "placeholder": "Observacoes (opcional)",
                "multiline": True,
            },
        ]

    @staticmethod
    def _component_dialog_fields() -> list[dict[str, Any]]:
        return [
            {
                "key": "name",
                "label": "Dados:",
                "placeholder": "Dados do componente",
                "required": True,
            },
            {"key": "category", "label": "Categoria:", "placeholder": "Categoria do componente"},
            {
                "key": "part_number",
                "label": "Modelo / Part Number:",
                "placeholder": "Ex.: BC547B, IRFZ44N",
            },
            {
                "key": "location",
                "label": "Localizacao:",
                "placeholder": "Ex.: Gaveta A3, Bandeja 2",
            },
            {
                "key": "unit_price",
                "label": "Valor Unitario (R$):",
                "placeholder": "Ex.: 12,50",
                "money": True,
            },
            {
                "key": "notes",
                "label": "Observacoes:",
                "placeholder": "Observacoes",
                "multiline": True,
            },
        ]
