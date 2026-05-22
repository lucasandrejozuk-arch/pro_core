from __future__ import annotations

import re

from PySide6.QtWidgets import QComboBox, QGroupBox, QTableWidget, QTabWidget, QWidget

_SOURCE_TEXT_PROP = "_i18n_source_text"
_SOURCE_PLACEHOLDER_PROP = "_i18n_source_placeholder"
_SOURCE_TOOLTIP_PROP = "_i18n_source_tooltip"
_SOURCE_WINDOW_TITLE_PROP = "_i18n_source_window_title"
_SOURCE_TITLE_PROP = "_i18n_source_title"
_SOURCE_TAB_TEXTS_PROP = "_i18n_source_tabs"
_SOURCE_COMBO_TEXTS_PROP = "_i18n_source_combo"
_SOURCE_HEADER_TEXTS_PROP = "_i18n_source_headers"


_PHRASE_PT_TO_EN = {
    "PRO CORE - Dashboard": "PRO CORE - Dashboard",
    "PRO CORE - Alterar senha": "PRO CORE - Change Password",
    "Assistencia tecnica": "Technical Service",
    "Entrar": "Sign In",
    "Esqueci minha senha": "I Forgot My Password",
    "Conectar/Reiniciar backend": "Connect/Restart Backend",
    "Conectando/Reiniciando...": "Connecting/Restarting...",
    "Exibir senha": "Show password",
    "Ocultar senha": "Hide password",
    "Lembrar usuario": "Remember user",
    "Informe email e senha.": "Provide email and password.",
    "Informe o email da conta.": "Provide the account email.",
    "Verificando conexao com o backend...": "Checking backend connection...",
    "Backend conectado.": "Backend connected.",
    "Backend indisponivel.": "Backend unavailable.",
    "Este usuario precisa definir uma senha propria antes de continuar.": "This user must define a new password before continuing.",
    "Alterar senha": "Change password",
    "Senha atual": "Current password",
    "Nova senha": "New password",
    "Confirmar nova senha": "Confirm new password",
    "Salvar senha": "Save password",
    "Salvando...": "Saving...",
    "Preencha todos os campos.": "Fill in all fields.",
    "A nova senha deve ter pelo menos 8 caracteres.": "The new password must have at least 8 characters.",
    "A confirmacao da senha nao confere.": "Password confirmation does not match.",
    "Acesso negado": "Access denied",
    "Seu perfil nao possui acesso a este modulo.": "Your profile does not have access to this module.",
    "Reinicio do sistema": "System restart",
    "Sair": "Exit",
    "Logout": "Log out",
    "Dashboard": "Dashboard",
    "Ordens de Servico": "Service Orders",
    "Ferramentas": "Tools",
    "Clientes": "Customers",
    "Equipamentos": "Equipment",
    "Estoque": "Inventory",
    "Area administrativa": "Administrative Area",
    "Setores": "Sectors",
    "Usuarios": "Users",
    "Acessos de recursos": "Resource Access",
    "Solicitacoes de senha": "Password Requests",
    "Logs/Auditoria": "Logs/Audit",
    "Configuracoes": "Settings",
    "Empresa": "Company",
    "Aparencia e interface": "Appearance and Interface",
    "Backup": "Backup",
    "Claro": "Light",
    "Escuro": "Dark",
    "Portugues brasileiro": "Brazilian Portuguese",
    "English (United States)": "English (United States)",
    "Salvar configuracoes": "Save settings",
    "Executar backup agora": "Run backup now",
    "Executando...": "Running...",
    "Backup automatico ativo": "Automatic backup enabled",
    "Intervalo em horas": "Interval in hours",
    "Pasta de backup": "Backup folder",
    "Ultimo backup: nunca": "Last backup: never",
    "Portal do cliente (navegador)": "Customer Portal (browser)",
    "Reiniciar backend local": "Restart local backend",
    "Reiniciando...": "Restarting...",
    "Fechar": "Close",
    "Editor": "Editor",
    "Fechar editor": "Close editor",
    "Atualizar": "Refresh",
    "Limpar selecao": "Clear selection",
    "Anterior": "Previous",
    "Proxima": "Next",
}

_PHRASE_EN_TO_PT = {value: key for key, value in _PHRASE_PT_TO_EN.items() if value}

_TOKEN_PT_TO_EN = {
    "configuracoes": "settings",
    "configuracao": "setting",
    "empresa": "company",
    "nome": "name",
    "email": "email",
    "telefone": "phone",
    "documento": "document",
    "tema": "theme",
    "idioma": "language",
    "escala": "scale",
    "status": "status",
    "salvar": "save",
    "salvando": "saving",
    "carregando": "loading",
    "carregado": "loaded",
    "conectado": "connected",
    "desconectado": "disconnected",
    "atualizando": "updating",
    "atualizado": "updated",
    "reinicio": "restart",
    "reiniciar": "restart",
    "servidor": "server",
    "interno": "internal",
    "externo": "external",
    "usuario": "user",
    "usuarios": "users",
    "cliente": "customer",
    "clientes": "customers",
    "ordem": "order",
    "ordens": "orders",
    "servico": "service",
    "servicos": "services",
    "tecnico": "technician",
    "tecnica": "technical",
    "ferramentas": "tools",
    "estoque": "inventory",
    "equipamentos": "equipment",
    "modulo": "module",
    "modulos": "modules",
    "acesso": "access",
    "negado": "denied",
    "erro": "error",
    "sucesso": "success",
    "aviso": "warning",
    "invalido": "invalid",
    "indisponivel": "unavailable",
    "aguarde": "please wait",
    "sessao": "session",
    "tempo": "time",
    "login": "login",
    "perfil": "role",
    "setor": "sector",
    "backup": "backup",
    "anexos": "attachments",
    "diagnostico": "diagnosis",
    "aprovacao": "approval",
    "aprovada": "approved",
    "reprovada": "rejected",
    "pendente": "pending",
    "concluida": "completed",
    "encerrada": "closed",
    "limpar": "clear",
    "detalhes": "details",
}

_TOKEN_EN_TO_PT = {
    "settings": "configuracoes",
    "setting": "configuracao",
    "company": "empresa",
    "name": "nome",
    "phone": "telefone",
    "document": "documento",
    "theme": "tema",
    "language": "idioma",
    "scale": "escala",
    "status": "status",
    "save": "salvar",
    "saving": "salvando",
    "loading": "carregando",
    "loaded": "carregado",
    "connected": "conectado",
    "disconnected": "desconectado",
    "updating": "atualizando",
    "updated": "atualizado",
    "restart": "reinicio",
    "server": "servidor",
    "internal": "interno",
    "external": "externo",
    "user": "usuario",
    "users": "usuarios",
    "customer": "cliente",
    "customers": "clientes",
    "order": "ordem",
    "orders": "ordens",
    "service": "servico",
    "services": "servicos",
    "technician": "tecnico",
    "technical": "tecnica",
    "tools": "ferramentas",
    "inventory": "estoque",
    "equipment": "equipamentos",
    "module": "modulo",
    "modules": "modulos",
    "access": "acesso",
    "denied": "negado",
    "error": "erro",
    "success": "sucesso",
    "warning": "aviso",
    "invalid": "invalido",
    "unavailable": "indisponivel",
    "session": "sessao",
    "time": "tempo",
    "role": "perfil",
    "sector": "setor",
    "attachments": "anexos",
    "diagnosis": "diagnostico",
    "approval": "aprovacao",
    "approved": "aprovada",
    "rejected": "reprovada",
    "pending": "pendente",
    "completed": "concluida",
    "closed": "encerrada",
    "clear": "limpar",
    "details": "detalhes",
}


def normalize_language(language: str | None) -> str:
    normalized = str(language or "pt-BR").strip() or "pt-BR"
    if normalized not in {"pt-BR", "en-US"}:
        return "pt-BR"
    return normalized


def translate_ui_text(message: str, language: str | None = "pt-BR") -> str:
    normalized_language = normalize_language(language)
    text = str(message or "")
    if not text:
        return ""

    if normalized_language == "pt-BR":
        return _translate_to_pt_br(text)

    return _translate_to_en_us(text)


def apply_language_to_widgets(language: str | None, *roots: QWidget | None) -> None:
    normalized_language = normalize_language(language)
    for root in roots:
        if root is None:
            continue
        _apply_language_to_widget(root, normalized_language)
        for child in root.findChildren(QWidget):
            _apply_language_to_widget(child, normalized_language)


def _apply_language_to_widget(widget: QWidget, language: str) -> None:
    _translate_text_property(widget, language)
    _translate_placeholder_property(widget, language)
    _translate_tooltip_property(widget, language)
    _translate_window_title_property(widget, language)
    _translate_title_property(widget, language)
    _translate_tab_widget(widget, language)
    _translate_combo_widget(widget, language)
    _translate_table_headers(widget, language)


def _translate_text_property(widget: QWidget, language: str) -> None:
    text_getter = getattr(widget, "text", None)
    text_setter = getattr(widget, "setText", None)
    if not callable(text_getter) or not callable(text_setter):
        return
    source = widget.property(_SOURCE_TEXT_PROP)
    if source is None:
        source = str(text_getter() or "")
        widget.setProperty(_SOURCE_TEXT_PROP, source)
    text_setter(translate_ui_text(str(source), language))


def _translate_placeholder_property(widget: QWidget, language: str) -> None:
    placeholder_getter = getattr(widget, "placeholderText", None)
    placeholder_setter = getattr(widget, "setPlaceholderText", None)
    if not callable(placeholder_getter) or not callable(placeholder_setter):
        return
    source = widget.property(_SOURCE_PLACEHOLDER_PROP)
    if source is None:
        source = str(placeholder_getter() or "")
        widget.setProperty(_SOURCE_PLACEHOLDER_PROP, source)
    placeholder_setter(translate_ui_text(str(source), language))


def _translate_tooltip_property(widget: QWidget, language: str) -> None:
    source = widget.property(_SOURCE_TOOLTIP_PROP)
    if source is None:
        source = str(widget.toolTip() or "")
        widget.setProperty(_SOURCE_TOOLTIP_PROP, source)
    widget.setToolTip(translate_ui_text(str(source), language))


def _translate_window_title_property(widget: QWidget, language: str) -> None:
    title_getter = getattr(widget, "windowTitle", None)
    title_setter = getattr(widget, "setWindowTitle", None)
    if not callable(title_getter) or not callable(title_setter):
        return
    source = widget.property(_SOURCE_WINDOW_TITLE_PROP)
    if source is None:
        source = str(title_getter() or "")
        widget.setProperty(_SOURCE_WINDOW_TITLE_PROP, source)
    title_setter(translate_ui_text(str(source), language))


def _translate_title_property(widget: QWidget, language: str) -> None:
    if not isinstance(widget, QGroupBox):
        return
    source = widget.property(_SOURCE_TITLE_PROP)
    if source is None:
        source = str(widget.title() or "")
        widget.setProperty(_SOURCE_TITLE_PROP, source)
    widget.setTitle(translate_ui_text(str(source), language))


def _translate_tab_widget(widget: QWidget, language: str) -> None:
    if not isinstance(widget, QTabWidget):
        return
    source_tabs = widget.property(_SOURCE_TAB_TEXTS_PROP)
    if not isinstance(source_tabs, list) or len(source_tabs) != widget.count():
        source_tabs = [widget.tabText(index) for index in range(widget.count())]
        widget.setProperty(_SOURCE_TAB_TEXTS_PROP, source_tabs)
    for index, source_text in enumerate(source_tabs):
        widget.setTabText(index, translate_ui_text(str(source_text), language))


def _translate_combo_widget(widget: QWidget, language: str) -> None:
    if not isinstance(widget, QComboBox):
        return
    source_items = widget.property(_SOURCE_COMBO_TEXTS_PROP)
    if not isinstance(source_items, list) or len(source_items) != widget.count():
        source_items = [widget.itemText(index) for index in range(widget.count())]
        widget.setProperty(_SOURCE_COMBO_TEXTS_PROP, source_items)
    for index, source_text in enumerate(source_items):
        widget.setItemText(index, translate_ui_text(str(source_text), language))


def _translate_table_headers(widget: QWidget, language: str) -> None:
    if not isinstance(widget, QTableWidget):
        return
    source_headers = widget.property(_SOURCE_HEADER_TEXTS_PROP)
    if not isinstance(source_headers, list) or len(source_headers) != widget.columnCount():
        source_headers = []
        for column in range(widget.columnCount()):
            item = widget.horizontalHeaderItem(column)
            source_headers.append(item.text() if item else "")
        widget.setProperty(_SOURCE_HEADER_TEXTS_PROP, source_headers)
    for column, source_text in enumerate(source_headers):
        item = widget.horizontalHeaderItem(column)
        if item is None:
            continue
        item.setText(translate_ui_text(str(source_text), language))


def _translate_to_pt_br(text: str) -> str:
    direct = _PHRASE_EN_TO_PT.get(text)
    if direct:
        return direct
    return _apply_token_translation(text, _TOKEN_EN_TO_PT)


def _translate_to_en_us(text: str) -> str:
    direct = _PHRASE_PT_TO_EN.get(text)
    if direct:
        return direct
    return _apply_token_translation(text, _TOKEN_PT_TO_EN)


def _apply_token_translation(text: str, token_map: dict[str, str]) -> str:
    if not text.strip():
        return text

    translated = text
    # Preserve separators and translate token by token.
    tokens = re.split(r"(\W+)", translated, flags=re.UNICODE)
    output: list[str] = []
    for token in tokens:
        if not token or re.fullmatch(r"\W+", token, flags=re.UNICODE):
            output.append(token)
            continue
        mapped = token_map.get(token.lower())
        if not mapped:
            output.append(token)
            continue
        output.append(_apply_case(mapped, token))

    return "".join(output)


def _apply_case(target: str, source: str) -> str:
    if source.isupper():
        return target.upper()
    if source.istitle():
        return target.title()
    return target
