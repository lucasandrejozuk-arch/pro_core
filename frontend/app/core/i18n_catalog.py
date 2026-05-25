from __future__ import annotations

SOURCE_TEXT_PROP = "_i18n_source_text"
SOURCE_PLACEHOLDER_PROP = "_i18n_source_placeholder"
SOURCE_TOOLTIP_PROP = "_i18n_source_tooltip"
SOURCE_WINDOW_TITLE_PROP = "_i18n_source_window_title"
SOURCE_TITLE_PROP = "_i18n_source_title"
SOURCE_TAB_TEXTS_PROP = "_i18n_source_tabs"
SOURCE_COMBO_TEXTS_PROP = "_i18n_source_combo"
SOURCE_HEADER_TEXTS_PROP = "_i18n_source_headers"

PHRASE_PT_TO_EN = {
    "PRO CORE - Dashboard": "PRO CORE - Dashboard",
    "PRO CORE - Alterar senha": "PRO CORE - Change Password",
    "Assistencia tecnica": "Technical Service",
    "Painel Principal": "Main Panel",
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
    "Este usuario precisa definir uma senha propria antes de continuar.": (
        "This user must define a new password before continuing."
    ),
    "Alterar senha": "Change password",
    "Senha atual": "Current password",
    "Nova senha": "New password",
    "Confirmar nova senha": "Confirm new password",
    "Salvar senha": "Save password",
    "Salvando...": "Saving...",
    "Preencha todos os campos.": "Fill in all fields.",
    "A nova senha deve ter pelo menos 8 caracteres.": (
        "The new password must have at least 8 characters."
    ),
    "A confirmacao da senha nao confere.": "Password confirmation does not match.",
    "Acesso negado": "Access denied",
    "Seu perfil nao possui acesso a este modulo.": (
        "Your profile does not have access to this module."
    ),
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
    "CONFIGURACOES DO SISTEMA": "SYSTEM SETTINGS",
    "Empresa": "Company",
    "Aparencia e interface": "Appearance and Interface",
    "Aparencia": "Appearance",
    "APARENCIA": "APPEARANCE",
    "Interface": "Interface",
    "INTERFACE": "INTERFACE",
    "Backup": "Backup",
    "BACKUP E RETENCAO": "BACKUP AND RETENTION",
    "DADOS DA EMPRESA": "COMPANY DETAILS",
    "Claro": "Light",
    "Escuro": "Dark",
    "Portugues brasileiro": "Brazilian Portuguese",
    "English (United States)": "English (United States)",
    "Razao social": "Legal name",
    "Nome fantasia": "Trade name",
    "Nome exibido no sistema": "Display name in the system",
    "Subtitulo da empresa": "Company subtitle",
    "Nome exibido": "Display name",
    "Subtitulo": "Subtitle",
    "Paleta": "Palette",
    "Capa do login": "Login cover",
    "Imagem": "Image",
    "Original do sistema": "System default",
    "Circuito tecnico": "Technical circuit",
    "Bancada premium": "Premium workbench",
    "Grade de precisao": "Precision grid",
    "Imagem anexada": "Attached image",
    "Selecionar imagem PNG/JPEG": "Select PNG/JPEG image",
    "Remover anexo": "Remove attachment",
    "Capa original quando o backend estiver offline.": (
        "The default cover is used when the backend is offline."
    ),
    "Idioma": "Language",
    "Escala da interface": "Interface scale",
    "Salvar configuracoes": "Save settings",
    "Salvar": "Save",
    "Cancelar": "Cancel",
    "Executar backup agora": "Run backup now",
    "Executando...": "Running...",
    "Backup automatico ativo": "Automatic backup enabled",
    "Frequencia": "Frequency",
    "Horas": "Hours",
    "Dias": "Days",
    "Semanas": "Weeks",
    "Destino": "Destination",
    "Caminho": "Path",
    "Pasta interna do Pro Core": "Internal Pro Core folder",
    "Local personalizado": "Custom location",
    "Selecionar pasta": "Select folder",
    "Selecione uma pasta personalizada": "Select a custom folder",
    "Intervalo em horas": "Interval in hours",
    "Pasta de backup": "Backup folder",
    "Defina a frequencia, a escala de tempo e onde os arquivos serao gravados.": (
        "Set the frequency, time scale and where the files will be stored."
    ),
    "Selecionar pasta de backup": "Select backup folder",
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
    "Dados": "Data",
    "Dados completos": "Full details",
    "DADOS COMPLETOS": "FULL DETAILS",
    "Resumo do item selecionado": "Summary of the selected item",
    "Nenhum item selecionado.": "No item selected.",
    "Selecione um modulo para carregar dados.": "Select a module to load data.",
    "Empresa em foco: revise cadastro, documento e canais de contato.": (
        "Company in focus: review registration, document and contact channels."
    ),
    "Aparencia em foco: ajuste marca, paleta e capa do login.": (
        "Appearance in focus: adjust brand, palette and login cover."
    ),
    "Interface em foco: confirme idioma e escala antes de aplicar.": (
        "Interface in focus: confirm language and scale before applying."
    ),
    "Backup em foco: valide frequencia, destino e ultimo ciclo.": (
        "Backup in focus: validate frequency, destination and last cycle."
    ),
    "Configuracoes em foco: revise os dados antes de salvar.": (
        "Settings in focus: review the data before saving."
    ),
    "Retome o backup: confirme a agenda e o destino antes de salvar.": (
        "Resume backup: confirm the schedule and destination before saving."
    ),
    "Acesso rapido: informe seu email para continuar.": (
        "Quick access: enter your email to continue."
    ),
    "Email identificado. Agora informe sua senha para entrar.": (
        "Email identified. Now enter your password to sign in."
    ),
    "Tudo pronto. Pressione Enter ou clique em Entrar.": (
        "Everything is ready. Press Enter or click Sign In."
    ),
    (
        "O backend esta indisponivel no momento. Use Inicializar/Reinicializar Backend "
        "para restabelecer o acesso."
    ): (
        "The backend is unavailable right now. Use Initialize/Restart Backend to restore access."
    ),
    "Inicializar/Reinicializar Backend": "Initialize/Restart Backend",
    "Inicializando/Reiniciando...": "Initializing/Restarting...",
    "Tentando inicializar/reinicializar backend...": (
        "Trying to initialize/restart the backend..."
    ),
    "Backend iniciado/reiniciado. Aguarde alguns instantes para concluir a conexao.": (
        "Backend started/restarted. Wait a few moments for the connection to finish."
    ),
    "Nao foi possivel conectar ao backend. Tente novamente em instantes.": (
        "Could not connect to the backend. Try again in a moment."
    ),
    "Inicia o backend local ou aplica reinicializacao segura quando possivel.": (
        "Starts the local backend or applies a safe restart when possible."
    ),
    "Nenhum resultado nesta busca. Ajuste os termos ou limpe o filtro para voltar ao fluxo.": (
        "No results for this search. Adjust the terms or clear the filter to return to the flow."
    ),
    "Comece pela base de clientes. Abra o Editor para cadastrar o primeiro cliente.": (
        "Start with the customer base. Open the Editor to register the first customer."
    ),
    "Selecione um cliente para revisar dados ou abra o Editor para um novo cadastro.": (
        "Select a customer to review data or open the Editor for a new record."
    ),
    "Cliente em foco. Revise os dados, salve ajustes ou envie um anexo.": (
        "Customer in focus. Review the data, save changes or send an attachment."
    ),
    "Crie o primeiro item para liberar controles de reposicao e movimentacao.": (
        "Create the first item to unlock replenishment and movement controls."
    ),
    "Selecione um item para revisar estoque ou crie um novo cadastro.": (
        "Select an item to review stock or create a new record."
    ),
    "Item em foco. Revise saldo, custo e anexos antes de salvar.": (
        "Item in focus. Review balance, cost and attachments before saving."
    ),
    "Sem OS no momento. Abra o Editor para registrar uma nova entrada.": (
        "No service orders at the moment. Open the Editor to register a new intake."
    ),
    "Selecione uma OS para continuar o fluxo tecnico ou abra o Editor para uma nova entrada.": (
        "Select a service order to continue the technical flow or open the Editor for a new intake."
    ),
    "OS em foco. Atualize diagnostico, orcamento e andamento no mesmo fluxo.": (
        "Service order in focus. Update diagnosis, quote and progress in the same flow."
    ),
    "Cadastre setores para organizar equipes e permissoes.": (
        "Register sectors to organize teams and permissions."
    ),
    "Selecione um setor para revisar estrutura e responsaveis.": (
        "Select a sector to review structure and owners."
    ),
    "Cadastre usuarios para distribuir acesso operacional.": (
        "Register users to distribute operational access."
    ),
    "Selecione um usuario para revisar perfil, setor e acesso.": (
        "Select a user to review role, sector and access."
    ),
    "Defina acessos por conta para liberar cada modulo.": (
        "Define access by account to unlock each module."
    ),
    "Selecione um acesso para revisar permissoes antes de salvar.": (
        "Select an access rule to review permissions before saving."
    ),
    "Nenhuma solicitacao pendente. Quando surgir uma, revise por aqui.": (
        "No pending request. When one appears, review it here."
    ),
    "Selecione uma solicitacao para resolver o acesso com seguranca.": (
        "Select a request to resolve access safely."
    ),
    "Os registros de auditoria aparecerao aqui conforme o uso do sistema.": (
        "Audit records will appear here as the system is used."
    ),
    "Selecione um evento para revisar contexto, usuario e impacto operacional.": (
        "Select an event to review context, user and operational impact."
    ),
    "Registro em foco. Revise os detalhes e confirme a proxima acao.": (
        "Record in focus. Review the details and confirm the next action."
    ),
    "Nenhum registro carregado ainda. Abra o Editor para iniciar este fluxo.": (
        "No record loaded yet. Open the Editor to start this flow."
    ),
    "Selecione um registro para revisar detalhes ou abra o Editor para uma nova acao.": (
        "Select a record to review details or open the Editor for a new action."
    ),
    "Pagina 1 de 1": "Page 1 of 1",
    "Sessao: -": "Session: -",
    "Backend: verificando": "Backend: checking",
    "Servidor interno: pendente": "Internal server: pending",
    "Area Administrativa": "Administrative Area",
    "Acesse configuracoes e rotinas administrativas.": (
        "Access settings and administrative routines."
    ),
    "Setores e estrutura operacional.": "Sectors and operational structure.",
    "Usuarios, perfis e redefinicao de senha.": "Users, roles and password reset.",
    "Solicitacoes de recuperacao de acesso.": "Access recovery requests.",
    "Acessos de recursos por conta e modulo.": "Resource access by account and module.",
    "Identidade visual, empresa, tema e backup.": "Branding, company, theme and backup.",
    "Rastreabilidade administrativa e operacional.": "Administrative and operational traceability.",
    (
        "Idioma alterado. Para garantir 100% de cobertura da traducao em toda a "
        "interface, reinicie o frontend agora."
    ): (
        "Language changed. To ensure full translation coverage across the interface, "
        "restart the frontend now."
    ),
    "Reiniciar agora": "Restart now",
    "Reiniciar depois": "Restart later",
    (
        "Idioma e escala local da interface. A troca de idioma aplica os textos "
        "dinamicos e mensagens operacionais do sistema."
    ): (
        "Local interface language and scale. Changing the language applies the dynamic "
        "texts and operational messages across the system."
    ),
    "Status: carregue configuracoes para revisar identidade e interface.": (
        "Status: load settings to review identity and interface."
    ),
    "Carregando configuracoes da empresa e preferencias visuais.": (
        "Loading company settings and visual preferences."
    ),
    "Backup: carregando intervalo, escala e destino configurados.": (
        "Backup: loading configured interval, scale and destination."
    ),
    "Configuracoes ainda nao carregadas. Revise empresa, aparencia e backup.": (
        "Settings not loaded yet. Review company, appearance and backup."
    ),
    "Backup: informe intervalo, escala e destino antes de salvar.": (
        "Backup: provide interval, scale and destination before saving."
    ),
    "Configuracoes carregadas.": "Settings loaded.",
    "Nenhuma alteracao pendente.": "No pending changes.",
    "Informe o nome da empresa.": "Provide the company name.",
    "Informe um email valido.": "Provide a valid email.",
    "Intervalo de backup deve ficar entre 1 e 720 horas.": (
        "Backup interval must be between 1 and 720 hours."
    ),
    "Informe o intervalo de backup.": "Provide the backup interval.",
    "Informe a pasta de backup.": "Provide the backup folder.",
    "Identidade": "Identity",
    "Tema": "Theme",
    "Escala": "Scale",
    "ativo": "active",
    "inativo": "inactive",
    "intervalo": "interval",
    "destino": "destination",
    "ultimo": "last",
    "NOVO CASO DE DEFEITO": "NEW DEFECT CASE",
    "EDITAR CASO DE DEFEITO": "EDIT DEFECT CASE",
    "(Sem objeto especifico)": "(No linked object)",
    "Objeto vinculado": "Linked object",
    "Titulo:": "Title:",
    "Sintoma:": "Symptom:",
    "Causa raiz:": "Root cause:",
    "Solucao:": "Solution:",
    "Observacoes:": "Notes:",
    "Ex.: Falha de comunicacao do modulo": "E.g.: Module communication failure",
    "Descreva sintomas observados": "Describe observed symptoms",
    "Descreva a causa raiz": "Describe the root cause",
    "Descreva a solucao aplicada": "Describe the applied solution",
    "Observacoes adicionais (opcional)": "Additional notes (optional)",
    "Informe o titulo.": "Provide the title.",
    "+Caso de Defeito": "+Defect Case",
    "Buscar casos de defeito...": "Search defect cases...",
    "TITULO": "TITLE",
    "SINTOMA": "SYMPTOM",
    "CAUSA RAIZ": "ROOT CAUSE",
    "ATUALIZADO": "UPDATED",
    "Editar": "Edit",
    "Remover": "Remove",
    "RESUMO:": "SUMMARY:",
    "Selecione um caso para ver detalhes.": "Select a case to view details.",
    "Nenhum caso encontrado.": "No case found.",
    "Esta acao nao pode ser desfeita.": "This action cannot be undone.",
    "Excluir": "Delete",
}
PHRASE_EN_TO_PT = {value: key for key, value in PHRASE_PT_TO_EN.items() if value}

TOKEN_PT_TO_EN = {
    "configuracoes": "settings",
    "configuracao": "setting",
    "painel": "panel",
    "principal": "main",
    "identidade": "identity",
    "empresa": "company",
    "nome": "name",
    "email": "email",
    "telefone": "phone",
    "documento": "document",
    "dados": "data",
    "tema": "theme",
    "claro": "light",
    "escuro": "dark",
    "idioma": "language",
    "escala": "scale",
    "status": "status",
    "selecione": "select",
    "carregar": "load",
    "pagina": "page",
    "item": "item",
    "salvar": "save",
    "cancelar": "cancel",
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
    "ativo": "active",
    "inativo": "inactive",
    "anexos": "attachments",
    "diagnostico": "diagnosis",
    "aprovacao": "approval",
    "aprovada": "approved",
    "reprovada": "rejected",
    "concluida": "completed",
    "encerrada": "closed",
    "limpar": "clear",
    "detalhes": "details",
    "acessar": "access",
    "rotinas": "routines",
    "administrativas": "administrative",
    "aparencia": "appearance",
    "retencao": "retention",
    "imagem": "image",
    "selecionar": "select",
    "remover": "remove",
    "anexo": "attachment",
    "titulo": "title",
    "sintoma": "symptom",
    "causa": "cause",
    "raiz": "root",
    "solucao": "solution",
    "observacoes": "notes",
    "caso": "case",
    "defeito": "defect",
    "buscar": "search",
    "pendente": "pending",
    "completos": "full",
}

TOKEN_EN_TO_PT = {
    "settings": "configuracoes",
    "setting": "configuracao",
    "panel": "painel",
    "main": "principal",
    "company": "empresa",
    "name": "nome",
    "phone": "telefone",
    "document": "documento",
    "data": "dados",
    "theme": "tema",
    "language": "idioma",
    "scale": "escala",
    "identity": "identidade",
    "status": "status",
    "select": "selecione",
    "load": "carregar",
    "page": "pagina",
    "item": "item",
    "save": "salvar",
    "cancel": "cancelar",
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
    "light": "claro",
    "dark": "escuro",
    "active": "ativo",
    "inactive": "inativo",
    "interval": "intervalo",
    "destination": "destino",
    "last": "ultimo",
    "routines": "rotinas",
    "administrative": "administrativas",
    "appearance": "aparencia",
    "retention": "retencao",
    "image": "imagem",
    "remove": "remover",
    "attachment": "anexo",
    "title": "titulo",
    "symptom": "sintoma",
    "cause": "causa",
    "root": "raiz",
    "solution": "solucao",
    "notes": "observacoes",
    "case": "caso",
    "defect": "defeito",
    "search": "buscar",
    "full": "completos",
}
