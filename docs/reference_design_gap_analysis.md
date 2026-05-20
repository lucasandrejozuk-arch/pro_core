# PRO TECHNICAL TOOLS 1.4 Reference Analysis

Referência local: `C:\Users\Lucas\Documents\vscode_projects\pro_tech_tools_1.4`

## Direção Visual

- Navegação lateral compacta e focada por módulo.
- Uso de ícones por módulo e ações.
- Layout operacional denso, sem dashboard ocupando todos os módulos.
- Componentes compartilhados para tabelas, detalhes, diálogos e visualizadores.
- Tema claro/escuro com tokens de design.
- Separação entre navegação, conteúdo, status e ações.

## Funcionalidades Presentes na Referência e Ausentes ou Parciais no PRO CORE

- Calculadora técnica.
- Assistente IA local.
- Chat/histórico operacional.
- Compras.
- Orçamentos como módulo próprio sincronizado com OS.
- Casos de defeito vinculados a equipamentos/placas.
- Auditoria operacional avançada com trilha estruturada.
- Importação/exportação avançada por módulo.
- Diagnóstico em tempo real/logs operacionais.
- Timeout de sessão por inatividade.
- Bloqueio temporário após tentativas inválidas.
- Empacotamento Windows com instalador.

## Etapas Recomendadas

1. Fundação funcional
   - Dashboard como módulo independente.
   - Clientes com validação e anexos.
   - Equipamentos com número especial, placas e componentes.
   - Matriz profissional de testes.

2. Refatoração visual segura
   - Extrair componentes Qt compartilhados.
   - Recriar sidebar e header usando estilo da referência.
   - Aplicar tokens de tema no PRO CORE.
   - Manter contratos de API intactos.

3. Módulos complementares
   - Calculadora técnica.
   - Compras.
   - Orçamentos independentes.
   - Casos de defeito.

4. Segurança e operação
   - Auditoria avançada.
   - Timeout de sessão.
   - Bloqueio de login.
   - Empacotamento Windows.
