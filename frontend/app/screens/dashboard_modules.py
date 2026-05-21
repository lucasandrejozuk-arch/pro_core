from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleStage:
    key: str
    stage: int
    label: str
    description: str
    action_hint: str
    group: str
    icon_name: str
    searchable: bool = False
    record_module: bool = False
    admin_only: bool = False
    manager_visible: bool = False


MODULE_STAGES: tuple[ModuleStage, ...] = (
    ModuleStage(
        key="dashboard",
        stage=1,
        label="Dashboard",
        description="Indicadores operacionais e alertas do dia",
        action_hint="Acompanhe pendencias e entre nos modulos pelos indicadores.",
        group="OPERACAO",
        icon_name="dashboard",
    ),
    ModuleStage(
        key="service_orders",
        stage=2,
        label="Ordens de Servico",
        description="Fluxo operacional de ordens de servico",
        action_hint="Priorize, diagnostique, aprove orcamentos e conclua atendimentos.",
        group="OPERACAO",
        icon_name="service_orders",
        searchable=True,
        record_module=True,
    ),
    ModuleStage(
        key="tools",
        stage=3,
        label="Ferramentas",
        description="Calculadoras e utilitarios por perfil operacional",
        action_hint="Use ferramentas tecnicas sem sair do contexto de atendimento.",
        group="OPERACAO",
        icon_name="tools",
    ),
    ModuleStage(
        key="customers",
        stage=4,
        label="Clientes",
        description="Cadastro e relacionamento de clientes",
        action_hint="Mantenha contatos, enderecos, observacoes e anexos atualizados.",
        group="CADASTROS",
        icon_name="customers",
        searchable=True,
        record_module=True,
        manager_visible=True,
    ),
    ModuleStage(
        key="equipment",
        stage=5,
        label="Equipamentos",
        description="Gestao hierarquica de ativos, objetos e componentes",
        action_hint="Cadastre equipamentos, objetos vinculados, componentes e casos de defeito.",
        group="CADASTROS",
        icon_name="equipment",
    ),
    ModuleStage(
        key="inventory",
        stage=6,
        label="Estoque",
        description="Estoque, custos e niveis minimos",
        action_hint="Controle pecas, custos e itens abaixo do minimo operacional.",
        group="CADASTROS",
        icon_name="inventory",
        searchable=True,
        record_module=True,
    ),
    ModuleStage(
        key="admin_area",
        stage=7,
        label="Area administrativa",
        description="Central de administracao, usuarios e auditoria",
        action_hint="Acesse as etapas administrativas permitidas ao seu perfil.",
        group="ADMINISTRACAO",
        icon_name="admin",
        manager_visible=True,
    ),
    ModuleStage(
        key="sectors",
        stage=8,
        label="Setores",
        description="Setores, liderancas e estrutura operacional",
        action_hint="Organize setores para direcionar responsabilidades e acessos.",
        group="ADMINISTRACAO",
        icon_name="sectors",
        searchable=True,
        record_module=True,
        admin_only=True,
        manager_visible=True,
    ),
    ModuleStage(
        key="users",
        stage=9,
        label="Usuarios",
        description="Contas, perfis, setores e seguranca",
        action_hint="Gerencie contas, perfis, setores e redefinicoes manuais.",
        group="ADMINISTRACAO",
        icon_name="users",
        searchable=True,
        record_module=True,
        admin_only=True,
        manager_visible=True,
    ),
    ModuleStage(
        key="password_resets",
        stage=10,
        label="Solicitacoes de senha",
        description="Atendimento de solicitacoes de acesso",
        action_hint="Resolva solicitacoes pendentes e entregue senhas temporarias.",
        group="ADMINISTRACAO",
        icon_name="password_resets",
        searchable=True,
        record_module=True,
        admin_only=True,
        manager_visible=True,
    ),
    ModuleStage(
        key="audit_logs",
        stage=11,
        label="Logs/Auditoria",
        description="Rastreabilidade administrativa e operacional",
        action_hint="Revise eventos sensiveis e limpe registros quando necessario.",
        group="ADMINISTRACAO",
        icon_name="audit_logs",
        searchable=True,
        record_module=True,
        admin_only=True,
    ),
    ModuleStage(
        key="settings",
        stage=12,
        label="Configuracoes",
        description="Identidade visual, empresa, tema e backup",
        action_hint="Ajuste identidade, tema, escala local e rotina de backup.",
        group="ADMINISTRACAO",
        icon_name="settings",
        admin_only=True,
    ),
)

MODULE_STAGE_BY_KEY = {stage.key: stage for stage in MODULE_STAGES}
TOTAL_MODULE_STAGES = len(MODULE_STAGES)


def module_stage_label(module_key: str) -> str:
    stage = MODULE_STAGE_BY_KEY.get(module_key)
    if stage is None:
        return "Etapa"
    return f"Etapa {stage.stage} de {TOTAL_MODULE_STAGES}"

