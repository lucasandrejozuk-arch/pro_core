# Etapas operacionais por modulo

Esta sequencia define a ordem de consolidacao da experiencia operacional do PRO CORE.
Cada modulo deve evoluir como uma etapa independente, mantendo a barra superior, o rodape
de contexto, a navegacao lateral fixa e os padroes de lista/editor consistentes.

| Etapa | Modulo | Objetivo operacional |
| --- | --- | --- |
| 1 | Dashboard | Acompanhar indicadores, alertas e atalhos para os modulos criticos. |
| 2 | Ordens de Servico | Priorizar, diagnosticar, orcar, aprovar e concluir atendimentos. |
| 3 | Ferramentas | Usar calculadoras e utilitarios tecnicos no contexto do operador. |
| 4 | Clientes | Manter contatos, enderecos, observacoes e anexos atualizados. |
| 5 | Equipamentos | Gerenciar equipamentos, objetos vinculados, componentes e defeitos. |
| 6 | Estoque | Controlar pecas, custos e niveis minimos. |
| 7 | Area administrativa | Centralizar acesso as etapas administrativas permitidas. |
| 8 | Setores | Organizar estrutura operacional, liderancas e direcionamento. |
| 9 | Usuarios | Gerenciar contas, perfis, setores e redefinicoes manuais. |
| 10 | Solicitacoes de senha | Resolver solicitacoes pendentes e senhas temporarias. |
| 11 | Logs/Auditoria | Revisar eventos sensiveis e rastreabilidade operacional. |
| 12 | Configuracoes | Ajustar identidade, tema, escala local e rotina de backup. |

## Etapa 2 - Ordens de Servico

Consolidada a orientacao operacional do fluxo de OS:

- O editor exibe o proximo passo conforme o status atual.
- A trilha visual cobre triagem, diagnostico, orcamento, aprovacao, execucao e conclusao.
- As acoes de diagnostico, orcamento, aprovacao, inicio e conclusao passam a respeitar o status da OS.
- OS encerradas ou reprovadas deixam de expor acoes de fluxo indevidas.
- Anexos continuam disponiveis para OS selecionadas, pois fazem parte da evidencia operacional.

## Etapa 3 - Ferramentas

Consolidada a orientacao operacional das ferramentas:

- O modulo informa quantas ferramentas foram liberadas pelo backend para o perfil atual.
- A tela mostra as especialidades disponiveis, como Eletrica e Operacional.
- Cada especialidade exibe um resumo local de ferramentas habilitadas.
- O estado vazio deixa claro quando nenhum recurso foi liberado para o usuario.
- O historico por especialidade continua registrando os ultimos calculos executados.

## Etapa 4 - Clientes

Consolidada a orientacao operacional do cadastro de clientes:

- O editor informa quando o operador esta criando um novo cliente.
- Clientes selecionados mostram estado ativo/inativo com impacto operacional claro.
- O envio de anexos fica bloqueado ate existir cliente selecionado e arquivo escolhido.
- A tela diferencia anexo pendente, pronto para envio e cliente sem selecao.
- O resumo completo continua servindo como referencia rapida para atendimento e OS.

## Etapa 5 - Equipamentos

Consolidada a orientacao operacional da hierarquia de equipamentos:

- A tela informa quando nao ha equipamentos cadastrados ou quando uma busca nao retorna dados.
- Equipamento selecionado exibe contagem de objetos vinculados e componentes.
- A hierarquia mostra o objeto ou componente selecionado e orienta o proximo nivel de acao.
- Acoes de editar, remover, casos de defeito, objeto e componente seguem a selecao atual.
- Importacao e exportacao continuam disponiveis no nivel de equipamentos.

## Etapa 6 - Estoque

Consolidada a orientacao operacional do estoque:

- Itens selecionados mostram se o nivel esta operacional, critico ou sem minimo configurado.
- A tela calcula reposicao necessaria a partir de quantidade atual e minimo.
- O painel informa custo estimado de reposicao e valor atual imobilizado em estoque.
- O resumo completo inclui reposicao necessaria e valor em estoque.
- O fluxo de salvar, novo e excluir segue a selecao atual do item.

## Etapa 7 - Area administrativa

Consolidada a orientacao operacional da central administrativa:

- A central informa o escopo administrativo liberado para o perfil atual.
- Administradores veem acesso as etapas de setores, usuarios, solicitacoes e auditoria.
- Gestores veem apenas as etapas operacionais permitidas para apoio administrativo.
- Perfis sem permissao recebem estado visivel de bloqueio, sem expor atalhos indevidos.
- Cada atalho administrativo exibe etapa, nome do modulo e dica operacional consistente.

## Etapa 8 - Setores

Consolidada a orientacao operacional do cadastro de setores:

- A tela informa quantos setores foram carregados e qual acao o perfil pode executar.
- Administradores recebem orientacao de criacao, edicao e exclusao da estrutura operacional.
- Gestores mantem consulta liberada, com campos e acoes destrutivas bloqueadas.
- Setor selecionado exibe estado de edicao ou consulta conforme o perfil atual.
- O resumo completo continua mostrando nome, descricao e data de criacao do setor.

## Etapa 9 - Usuarios

Consolidada a orientacao operacional do cadastro de usuarios:

- A tela informa quantas contas foram carregadas antes da selecao.
- Usuario selecionado mostra nome, perfil, setor e estado ativo/inativo.
- Contas inativas recebem destaque operacional para revisao de acesso.
- O painel de seguranca diferencia senha inicial de novas contas e redefinicao manual.
- Contas com troca de senha pendente exibem essa pendencia no status de seguranca.

## Etapa 10 - Solicitacoes de senha

Consolidada a orientacao operacional das solicitacoes de senha:

- A lista informa quantas solicitacoes foram carregadas e quantas seguem pendentes.
- Solicitacao selecionada mostra solicitante e status de atendimento.
- Solicitações pendentes liberam a definicao de senha temporaria.
- Solicitações resolvidas bloqueiam a acao de redefinicao para evitar reprocessamento.
- O resumo completo exibe status traduzido e dados do solicitante.

## Etapa 11 - Logs/Auditoria

Consolidada a orientacao operacional de logs e auditoria:

- A lista informa quantos logs foram carregados e quantos eventos sao sensiveis.
- Evento selecionado mostra acao, entidade e ator em status visivel.
- Acoes destrutivas, redefinicoes, configuracoes e auditoria recebem destaque sensivel.
- O resumo completo explicita se o evento exige atencao de auditoria.
- A exclusao de log permanece disponivel apenas apos selecao valida e com aviso de retencao.

## Etapa 12 - Configuracoes

Consolidada a orientacao operacional das configuracoes:

- A tela resume identidade exibida, empresa, tema e escala atual da interface.
- O status de backup informa se a rotina esta ativa, intervalo, destino e ultimo backup.
- A escala local atualiza o status operacional ao ser ajustada pelo operador.
- O resumo completo registra que identidade, interface e backup foram revisados.
- Acoes de salvar configuracoes e executar backup seguem os controles ja existentes.

## Padrao de consolidacao

- Cada etapa deve ter titulo, descricao, dica operacional e estado visivel na barra superior.
- Modulos de registro devem manter busca, resumo do item selecionado, editor e limpeza de selecao.
- Modulos com tela propria devem preservar o mesmo contexto de etapa, refresh e rodape.
- Permissoes de visibilidade devem sair do codigo espalhado e usar o registro central de modulos.
- Ao concluir cada etapa, rodar `ruff check backend frontend scripts` e `pytest -q`.
