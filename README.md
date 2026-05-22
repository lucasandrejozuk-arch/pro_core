# PRO CORE

PRO CORE e uma plataforma desktop completa para assistencias tecnicas que querem operar com padrao profissional, velocidade e controle. O produto foi desenhado para centralizar operacao, estoque, clientes, equipamentos, ordens de servico e administracao em uma unica experiencia.

## O que o software entrega hoje

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

## Diferenciais de produto

- Interface desktop de alta legibilidade com foco operacional.
- Tema claro/escuro com paletas visuais configuraveis.
- Mensageria de status no rodape com feedback contextual e destaque visual.
- Fluxos de cadastro guiados para reduzir erro humano e retrabalho.
- Arquitetura modular para evolucao continua sem romper o fluxo principal.

## Seguranca e confiabilidade

- Autenticacao com token e controle de acesso por perfil.
- Permissoes por papeis (administrador, gestor, tecnico, cliente).
- Troca obrigatoria de senha no primeiro acesso quando aplicavel.
- Sanitizacao e validacao de payloads no backend com Pydantic.
- Upload de documentos com validacao de extensao e limite de tamanho configuravel.
- Isolamento de armazenamento de anexos por empresa.
- Auditoria para rastreabilidade administrativa.
- Backup operacional integrado no sistema e restauracao via script.

## Performance operacional

- Backend em FastAPI com respostas rapidas para uso diario.
- Frontend em PySide6 otimizado para produtividade em desktop.
- Filtros e listagens para reduzir tempo de localizacao de registros.
- Feedback imediato de erros e sucesso para diminuir ciclos de tentativa.

## Estilo visual e experiencia

- Linguagem visual tecnica e profissional.
- Densidade de informacao calibrada para operacao real.
- Estados de alerta, sucesso e erro padronizados.
- Rodape operacional com contexto de sessao, status do backend e mensagens de fluxo.

## Stack atual

- Backend: Python + FastAPI
- Frontend: Qt for Python (PySide6)
- Banco de dados: PostgreSQL
- Infra local: Docker Compose
- Migracoes: Alembic
- Testes: Pytest

## Como rodar localmente

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

## Backup e restauracao

- Backup via interface em Configuracoes, acao Executar backup agora.
- Caminho padrao de dumps: backups.
- Caminho padrao de anexos: storage/uploads.
- Restauracao local:
  - python scripts/restore_database_backup.py --dump-file .\backups\pro_core_YYYYMMDD_HHMMSS.dump

## Referencias de qualidade

- Estrategia de testes: docs/testing_strategy.md
- Analise de evolucao de design e escopo: docs/reference_design_gap_analysis.md

## Estado atual de idioma

- Idioma operacional ativo no produto: Portugues do Brasil (pt-BR).
