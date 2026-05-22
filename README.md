# PRO CORE

PRO CORE e uma plataforma desktop para assistencias tecnicas com backend FastAPI e frontend PySide6. O sistema centraliza atendimento, operacao de bancada, estoque, administracao, seguranca e governanca em um unico fluxo.

## Visao Geral

- Operacao completa de ordens de servico (entrada, diagnostico, orcamento, aprovacao, execucao e encerramento).
- Cadastro de clientes, equipamentos, estoque e documentos.
- Painel administrativo com usuarios, setores, acessos dinamicos, auditoria e configuracoes.
- Portal web do cliente para consulta e decisao de orcamento.
- Persistencia com PostgreSQL, migracoes com Alembic e suites de teste com Pytest.

## Funcionalidades Entregues

- Fluxo operacional de ordens de servico com status, aprovacao, diagnostico, orcamento e conclusao.
- Cadastro e historico de clientes com anexos.
- Gestao de equipamentos, objetos vinculados e componentes.
- Gestao de estoque com assistente em 3 etapas:
  - Etapa 1: submodulo e categoria.
  - Etapa 2: dados tecnicos dinamicos por categoria.
  - Etapa 3: observacoes, anexos PDF e lista de anexos vinculados com botao de download individual por arquivo.
- Submodulos de estoque: Componentes, Ferramentas e Softwares.
- Validacoes tecnicas por categoria para evitar cadastro incompleto.
- Modulo administrativo com usuarios, setores, solicitacoes de senha, auditoria e configuracoes.
- Dashboard com indicadores operacionais e alertas.
- IDs profissionais padronizados em listagens e resumos dos principais modulos.
- Controle de acesso por modulo e especialidade de ferramentas.
- Reinicio seguro do backend com autorizacao administrativa e aviso global.

## Experiencia, Idioma e Aparencia

- Interface desktop com foco em legibilidade e produtividade.
- Tema claro/escuro com paletas configuraveis por empresa.
- Escala visual ajustavel para diferentes resolucoes.
- Idiomas de configuracao disponiveis:
	- Portugues do Brasil (pt-BR)
	- English (United States) (en-US)

## Seguranca, Erro e Redundancia

- Autenticacao com token e controle de acesso por perfil.
- Permissoes por papeis (administrador, gestor, tecnico, cliente).
- Troca obrigatoria de senha no primeiro acesso quando aplicavel.
- Sanitizacao e validacao de payloads no backend com Pydantic.
- Upload de documentos com validacao de extensao e limite de tamanho configuravel.
- Isolamento de armazenamento de anexos por empresa.
- Auditoria para rastreabilidade administrativa.
- Backup operacional integrado no sistema e restauracao via script.
- Rate limiting em rotas sensiveis (login e portal do cliente).
- Cabecalhos de seguranca HTTP e CSP ativo.
- Tratamento de erro de ponta a ponta:
	- backend com HTTPException tipado por contexto de negocio
	- frontend com mensagens amigaveis e traducao para erros comuns
	- fallback de erro para nao expor detalhes internos
- Redundancia em chamadas HTTP no frontend para operacoes idempotentes:
	- retry automatico em falhas transientes de conexao/timeout
	- retry em erros 5xx para GET/HEAD/OPTIONS/DELETE
- Criacao de SKU com fallback e reintento para reduzir colisao em cenarios concorrentes.

## WhatsApp e Comunicacao

- Hoje, o sistema trabalha com dados de contato (email e telefone) no cadastro de clientes.
- O fluxo operacional permite padronizar o canal de comunicacao na camada de negocio (ex.: Email/WhatsApp) para registro e exibicao de contexto.
- O portal do cliente complementa a comunicacao por autoatendimento de orcamento.
- Lacunas atuais (importante):
	- nao existe integracao nativa com API oficial do WhatsApp (envio automatico de mensagens)
	- nao existe webhook de retorno de leitura/entrega de WhatsApp
	- nao existe fila interna dedicada para disparos omnichannel

## Performance Operacional

- Backend em FastAPI com respostas rapidas para uso diario.
- Frontend em PySide6 otimizado para produtividade em desktop.
- Filtros e listagens para reduzir tempo de localizacao de registros.
- Feedback imediato de erros e sucesso para diminuir ciclos de tentativa.

## Stack Tecnica

- Backend: Python + FastAPI
- Frontend: Qt for Python (PySide6)
- Banco de dados: PostgreSQL
- Infra local: Docker Compose
- Migracoes: Alembic
- Testes: Pytest

## Como Rodar Localmente

1. Criar e ativar ambiente virtual:
	- python -m venv .venv
	- .\.venv\Scripts\Activate.ps1
	- python -m pip install --upgrade pip
	- python -m pip install -e ".[dev]"
2. Subir PostgreSQL:
	- docker compose up -d postgres
3. Aplicar migracoes:
	- alembic upgrade head
4. Criar administrador inicial:
	- python scripts/create_initial_admin.py --company-name "Minha Assistencia" --admin-name "Administrador" --email admin@example.com --password "ChangeMe123"
5. Iniciar backend:
	- uvicorn backend.app.main:app --reload
6. Iniciar frontend:
	- python frontend/app/main.py

## Backup e Restauracao

- Backup via interface em Configuracoes, acao Executar backup agora.
- Caminho padrao de dumps: backups.
- Caminho padrao de anexos: storage/uploads.
- Restauracao local:
  - python scripts/restore_database_backup.py --dump-file .\backups\pro_core_YYYYMMDD_HHMMSS.dump

## Testes

- Rodar backend (exemplo focado):
	- pytest backend/tests/test_commercial_workflow_routes.py backend/tests/test_app_health.py -q
- Rodar frontend (exemplo focado):
	- pytest frontend/tests/test_dashboard_window.py frontend/tests/test_dashboard_window_settings.py frontend/tests/test_api_client.py -q

## Referencias

- Estrategia de testes: docs/testing_strategy.md
- Analise de evolucao de design e escopo: docs/reference_design_gap_analysis.md
