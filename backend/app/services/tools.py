from __future__ import annotations

from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.tools import ToolDefinition

TECHNICAL_TOOLS = (
    ToolDefinition(
        id="ohm",
        name="Lei de Ohm",
        category="technical",
        module="calculators",
        description="Calcula tensao, corrente ou resistencia.",
        order=10,
    ),
    ToolDefinition(
        id="power",
        name="Potencia",
        category="technical",
        module="calculators",
        description="Calcula potencia eletrica por V/I/R.",
        order=20,
    ),
    ToolDefinition(
        id="led",
        name="LED",
        category="technical",
        module="calculators",
        description="Dimensiona resistor para LED.",
        order=30,
    ),
    ToolDefinition(
        id="divider",
        name="Divisor",
        category="technical",
        module="calculators",
        description="Calcula divisor resistivo.",
        order=40,
    ),
    ToolDefinition(
        id="battery",
        name="Bateria",
        category="technical",
        module="calculators",
        description="Estima autonomia de bateria.",
        order=50,
    ),
    ToolDefinition(
        id="resistor_color",
        name="Codigo de Cor de Resistores",
        category="technical",
        module="calculators",
        description="Decodifica resistor de quatro faixas.",
        order=60,
    ),
    ToolDefinition(
        id="resistor_assoc",
        name="Assoc. de Resistores",
        category="technical",
        module="calculators",
        description="Calcula associacao serie e paralelo.",
        order=70,
    ),
    ToolDefinition(
        id="awg",
        name="AWG/mm2",
        category="technical",
        module="calculators",
        description="Converte AWG para area em mm2.",
        order=80,
    ),
)

FINANCIAL_TOOLS = (
    ToolDefinition(
        id="markup",
        name="Markup",
        category="financial",
        module="finance",
        description="Calcula preco de venda por custo e margem.",
        order=110,
    ),
    ToolDefinition(
        id="installment",
        name="Parcelamento",
        category="financial",
        module="finance",
        description="Calcula parcela simples.",
        order=120,
    ),
)

MANAGEMENT_TOOLS = (
    ToolDefinition(
        id="sla",
        name="SLA",
        category="management",
        module="operations",
        description="Calcula prazo operacional em horas.",
        order=210,
    ),
    ToolDefinition(
        id="stock_reorder",
        name="Reposicao de Estoque",
        category="management",
        module="operations",
        description="Calcula necessidade de reposicao.",
        order=220,
    ),
)


def list_available_tools(user: User) -> list[ToolDefinition]:
    sector_name = (user.sector_name or "").strip().lower()
    role = user.role

    if role == UserRole.ADMIN:
        return _sorted_tools((*TECHNICAL_TOOLS, *FINANCIAL_TOOLS, *MANAGEMENT_TOOLS))

    if role == UserRole.MANAGER:
        if "finance" in sector_name:
            return _sorted_tools((*FINANCIAL_TOOLS, *MANAGEMENT_TOOLS))
        if "administr" in sector_name or "gest" in sector_name:
            return _sorted_tools((*TECHNICAL_TOOLS, *FINANCIAL_TOOLS, *MANAGEMENT_TOOLS))
        return _sorted_tools((*TECHNICAL_TOOLS, *MANAGEMENT_TOOLS))

    if role == UserRole.TECHNICIAN:
        if "finance" in sector_name:
            return _sorted_tools(FINANCIAL_TOOLS)
        return _sorted_tools(TECHNICAL_TOOLS)

    return []


def _sorted_tools(tools: tuple[ToolDefinition, ...]) -> list[ToolDefinition]:
    unique = {tool.id: tool for tool in tools}
    return sorted(unique.values(), key=lambda tool: tool.order)
