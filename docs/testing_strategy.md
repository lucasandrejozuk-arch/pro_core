# PRO CORE Testing Strategy

## Objetivo

Garantir que o MVP evolua com segurança para produto comercial, cobrindo regras de negócio, permissões, persistência, integrações locais e fluxos críticos do frontend Qt.

## Pirâmide de Testes

1. Unitários de domínio
   - Validação de schemas Pydantic.
   - Regras de escopo por perfil e setor.
   - Geração de códigos, totais e transições de status.
   - Normalização de email, telefone e campos obrigatórios.

2. Integração backend
   - Rotas FastAPI com banco isolado.
   - Migrações Alembic.
   - Upload/download de documentos.
   - Backup e restauração em ambiente controlado.
   - Relatórios e exportações.

3. Contrato frontend/backend
   - `ApiClient` cobrindo todos os endpoints usados pela UI.
   - Payloads obrigatórios, erros esperados e downloads.
   - Regressões para novos módulos.

4. UI Qt
   - Smoke test de criação das janelas principais.
   - Login, troca de senha e navegação de módulos.
   - Formulários com campos obrigatórios e máscaras.
   - Seleção de tabelas e preenchimento de formulários.
   - Objetos vinculados em equipamentos.

5. End-to-end local
   - Login admin.
   - Criar setor, gestor, técnico, cliente, equipamento, OS.
   - Fluxo completo da OS.
   - Upload de anexos.
   - Backup manual e validação.
   - Solicitação e resolução de senha.

## Gates Recomendados

Executar antes de cada release interna:

```powershell
python -m compileall backend frontend scripts
pytest
alembic upgrade head
alembic check
docker compose config --quiet
```

## Próximos Testes a Adicionar

- Testes Qt com `pytest-qt` para `DashboardWindow`, `LoginWindow` e `PasswordChangeWindow`.
- Teste real de backup/restauração usando PostgreSQL Docker.
- Testes de autorização negativa por módulo.
- Testes de anexos por cliente/equipamento além de OS.
- Testes de exportação PDF/XLSX com validação mínima de conteúdo.
- Testes de performance básica para listagens com volume simulado.
