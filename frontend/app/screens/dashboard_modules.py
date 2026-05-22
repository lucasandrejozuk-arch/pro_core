from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleDefinition:
    key: str
    label: str
    description: str
    group: str
    icon_name: str
    searchable: bool = False
    record_module: bool = False
    admin_only: bool = False
    manager_visible: bool = False


MODULE_DEFINITIONS: tuple[ModuleDefinition, ...] = (
    ModuleDefinition(
        key="dashboard",
        label="Dashboard",
        description="Indicadores operacionais e alertas do dia",
        group="OPERACAO",
        icon_name="dashboard",
    ),
    ModuleDefinition(
        key="service_orders",
        label="Ordens de Servico",
        description="Fluxo operacional de ordens de servico",
        group="OPERACAO",
        icon_name="service_orders",
        searchable=True,
        record_module=True,
    ),
    ModuleDefinition(
        key="tools",
        label="Ferramentas",
        description="Calculadoras e utilitarios por perfil operacional",
        group="OPERACAO",
        icon_name="tools",
    ),
    ModuleDefinition(
        key="customers",
        label="Clientes",
        description="Cadastro e relacionamento de clientes",
        group="CADASTROS",
        icon_name="customers",
        searchable=True,
        record_module=True,
        manager_visible=True,
    ),
    ModuleDefinition(
        key="equipment",
        label="Equipamentos",
        description="Gestao hierarquica de ativos, objetos e componentes",
        group="CADASTROS",
        icon_name="equipment",
    ),
    ModuleDefinition(
        key="inventory",
        label="Estoque",
        description="Estoque, custos e niveis minimos",
        group="CADASTROS",
        icon_name="inventory",
        searchable=True,
        record_module=True,
    ),
    ModuleDefinition(
        key="admin_area",
        label="Area administrativa",
        description="Central de administracao, usuarios e auditoria",
        group="ADMINISTRACAO",
        icon_name="admin",
        manager_visible=True,
    ),
    ModuleDefinition(
        key="sectors",
        label="Setores",
        description="Setores, liderancas e estrutura operacional",
        group="ADMINISTRACAO",
        icon_name="sectors",
        searchable=True,
        record_module=True,
        admin_only=True,
        manager_visible=True,
    ),
    ModuleDefinition(
        key="users",
        label="Usuarios",
        description="Contas, perfis, setores e seguranca",
        group="ADMINISTRACAO",
        icon_name="users",
        searchable=True,
        record_module=True,
        admin_only=True,
        manager_visible=True,
    ),
    ModuleDefinition(
        key="resource_access",
        label="Acessos de recursos",
        description="Permissoes por conta para recursos e modulos do sistema",
        group="ADMINISTRACAO",
        icon_name="users",
        searchable=True,
        record_module=True,
        admin_only=True,
        manager_visible=True,
    ),
    ModuleDefinition(
        key="password_resets",
        label="Solicitacoes de senha",
        description="Atendimento de solicitacoes de acesso",
        group="ADMINISTRACAO",
        icon_name="password_resets",
        searchable=True,
        record_module=True,
        admin_only=True,
        manager_visible=True,
    ),
    ModuleDefinition(
        key="audit_logs",
        label="Logs/Auditoria",
        description="Rastreabilidade administrativa e operacional",
        group="ADMINISTRACAO",
        icon_name="audit_logs",
        searchable=True,
        record_module=True,
        admin_only=True,
    ),
    ModuleDefinition(
        key="settings",
        label="Configuracoes",
        description="Identidade visual, empresa, tema e backup",
        group="ADMINISTRACAO",
        icon_name="settings",
        admin_only=True,
    ),
)

MODULE_BY_KEY = {module.key: module for module in MODULE_DEFINITIONS}
