# Execução — Sherlock Document Search

## Autorização e escopo

Em 25 de outubro de 2026, o usuário confirmou o plano e autorizou iniciar M1: “Confirmo o plano e autorizo iniciar o M1. Siga o recomendado, utilizando subagentes quando for benéfico.”

Arquétipo A — dados, análise e Quarto, identificado pelo escopo explícito do [plano aprovado](docs/plan.md). Condução contínua dentro dos marcos autorizados. O usuário aprovou o M1 e autorizou iniciar o M2; M3 foi posteriormente autorizado e concluído; M4–M6 não foram iniciados. A criação e manutenção do repositório GitHub fazem parte do contexto autorizado desta conversa; nenhum deploy de aplicação está incluído neste marco.

Linha de base: repositório limpo, apenas documentação de planejamento, sem pacote, testes ou manifests de implementação. Não havia suíte preexistente a executar nem dados originais versionados.

## Estado do M1

Implementado, validado tecnicamente e aprovado pelo usuário. O aceite e a autorização do M2 foram recebidos em 25 de outubro de 2026.

| Gate da execução | Evidência no M1 |
|---|---|
| Núcleo e contratos | Pacote Python sem dependências de execução; hashes e inventário estritos; parágrafos com linhas originais; dez testes incluindo regressões. |
| Integração e execução | Download público pelo código, nove TXT preparados e conferência de todos os 15.598 parágrafos contra as linhas de origem. |
| Apresentação e saídas | JSONL local com referências e JSON numérico de qualidade; nenhum dashboard ou figura era necessário ao M1. |
| Documentação | README, preparação, proveniência, manifesto e relatório numérico alinhados à execução. |
| Revisão integrada e build | Revisão independente, correção de dois achados, testes completos, sdist/wheel e instalação isolada com comparação das saídas. |

## Verificações executadas

- Antes da implementação, os testes falharam por ausência do módulo esperado. Depois, os testes sintéticos passaram e a integração real foi executada.
- `python -m sherlock_search --download`: obtenção pública validada por tamanho/hash do ZIP e dos nove TXT.
- `python -m unittest discover -s tests -v`: dez testes passaram com o corpus real, incluindo roundtrip de cada parágrafo.
- `uv build`: sdist e wheel construídos. Wheel instalado em ambiente Python 3.11.17 isolado, sem dependências de execução.
- Testes com o pacote instalado e execução da CLI fora da árvore do código-fonte; relatório e JSONL comparados byte a byte com a execução pelo código-fonte.
- Casos de erro da CLI conferidos: pasta de origem ausente, origem igual à saída e tentativa de repetir download sobre pasta existente; todos encerraram com mensagem clara, sem traceback nem escrita indevida.
- Verificação de diff e de exclusão dos dados no Git antes da entrega.

Ambientes de verificação: Linux; suíte completa em Python 3.15.0 pelo código-fonte e Python 3.11.17 pelo pacote instalado. Não foram testados Kaggle, Windows, macOS, GitHub Pages ou Community Cloud neste marco.

## Revisão e delegação

Dois subagentes com modelo mais leve inspecionaram proveniência e fronteiras editoriais. O agente principal conferiu limites, hashes e os resultados produzidos. Um terceiro subagente fez revisão independente de implementação e testes.

A revisão identificou dois marcadores `THE END` retidos e uma fração Unicode contada como palavra. Ambos foram corrigidos com testes de regressão; a revisão das correções não encontrou novos achados.

## Pendências e próximo marco

- As condições de uso e atribuição para publicar trechos ainda precisam ser verificadas; isso não impediu a preparação local nem a publicação de metadados e contagens.
- A limpeza mantém notas internas e alguns títulos editoriais. Não se implementou parser geral de capítulos ou contos.
- As 30 consultas do M2 foram propostas em dois arquivos separados e aprovadas pelo autor no chat. As vinte finais não foram executadas para ajustes, busca ou métricas.
- O próximo ponto de reestimativa do esforço será após a revisão humana em M2; a referência de 24 horas não foi convertida em garantia de prazo.
- M2 concluído: busca literal validada e 30 consultas aprovadas. A autorização do M3 foi recebida e executada; não iniciar M4 sem autorização para esse marco.

## Correção da pasta local

O usuário indicou `sherlock_holmes_series/` como pasta local do projeto. O checkout foi consolidado nessa pasta, preservando o histórico Git e os nove TXT que já existiam diretamente em `data/`. Seus hashes coincidem com o snapshot do M1. Esses TXT também ficam ignorados pelo Git; a cópia preparada continua em `data/raw/` e `data/processed/`. O ambiente virtual foi recriado no novo caminho para evitar referências ao local anterior.

Posteriormente, o usuário autorizou alinhar o nome da pasta local ao repositório GitHub. A pasta atual é `sherlock-document-search/`; a renomeação preservou o checkout e os dados. O ambiente virtual foi recriado e os testes do M1 foram conferidos no caminho definitivo.

## Execução do M2

Autorização explícita em 25 de outubro de 2026: “Já atualizei o caminho na configuração do projeto. Aprovo o M1 e autorizo iniciar o M2 conforme o plano, utilizando subagentes quando for benéfico.”

**Estado:** M2 concluído. Busca literal e preparação da revisão validadas tecnicamente; as 30 consultas foram aprovadas explicitamente pelo autor. M3 foi posteriormente autorizado e concluído, conforme o registro abaixo.

Linha de base: dez testes do M1, pacote instalado, snapshot de nove TXT identificado e checkout limpo no caminho definitivo `sherlock-document-search/`.

| Gate da execução | Evidência no M2 |
|---|---|
| Núcleo e contratos | Busca literal por palavra/expressão, até cinco resultados, score por ocorrências e desempate por arquivo/linhas. Validação das propostas de consulta sem executar recuperação. |
| Integração e execução | CLI preserva a preparação do M1 e acrescenta consulta e filtro. Integração real usa apenas um termo de desenvolvimento para conferir metadados, sem calcular qualidade. |
| Apresentação e saídas | Resultado textual com origem e contagem; mensagem de ausência. Dois arquivos Markdown locais mostram as fontes para o autor revisar. |
| Documentação | Regras da busca, instruções da revisão e protocolo de separação documentados; propostas continuam marcadas como pendentes. |
| Revisão integrada e build | 25 testes passaram, incluindo corpus real. Revisão independente corrigiu validação de tipos nos campos JSON. Build e execução do pacote instalado conferidos. |

### Consultas e separação

Dois subagentes com modelo mais leve propuseram os conjuntos sem usar rankings ou métricas. Desenvolvimento tem dez consultas (oito positivas e duas negativas propostas); final tem vinte (dezesseis positivas e quatro negativas propostas). Os tipos e a distribuição estão em [query-review.md](docs/query-review.md).

A proposta final foi mantida fora do contexto do agente implementador até a busca literal estar pronta no commit `a925735`. Após solicitação do autor, consultas e referências finais foram lidas para apresentação, sem mudar a busca ou executar métricas finais. O comando de revisão apenas confere estrutura e referências e gera arquivos para o autor; não executa busca. Os hashes em `evaluation/split_manifest.json` identificam as propostas, agora aprovados pelo autor. A versão dos rótulos está identificada; os parâmetros de TF-IDF serão fechados no M3 antes da avaliação final.

A revisão humana foi solicitada com links para os dois arquivos locais. Após esclarecer a apresentação das perguntas, o autor informou “pode continuar com aprovação das perguntas”. Registrou-se essa aprovação explícita nas 30 entradas, sem marcar uma inspeção individual não descrita pelo autor. As vinte consultas finais não foram usadas em testes de recuperação. O teste real da busca usa apenas um termo de desenvolvimento e verifica metadados, não acerto de rótulo.

### Verificações e limites

- Testes escritos antes da implementação falharam pela ausência dos novos módulos e passaram após implementar os contratos.
- Suíte completa de 25 testes: dez do M1, dez da busca/CLI e cinco da validação de revisão; corpus real incluído, sem testes ignorados.
- A revisão independente identificou que tipos JSON não textuais podiam gerar `TypeError`; a correção e o teste de regressão foram conferidos.
- Nenhuma métrica de qualidade foi calculada; o M2 verificou contratos e a separação dos conjuntos, com os rótulos aprovados ao final. Não há avaliação final ou TF-IDF neste marco.
- A revisão foi aprovada no chat, mas o tempo gasto pelo autor não foi medido. Não há base para converter a referência de 24 horas em prazo garantido; reavaliar ao iniciar M3.

A justificativa textual de `final-01` foi corrigida para descrever o ferimento em Maiwand. A consulta, o rótulo e a referência não mudaram, e a correção não se baseou em resultados de busca. O teste de integração percorreu somente as dez consultas de desenvolvimento para conferir limite e origem, sem calcular acurácia.

## Execução do M3

Em 25 de outubro de 2026, o usuário aprovou M2 e autorizou M3 “usando apenas as dez consultas de desenvolvimento para ajustes e mantendo as vinte finais reservadas para o M4”. Também perguntou sobre custo/benefício da skill Graphify.

**Estado:** M3 implementado e validado tecnicamente, com configuração e ativos congelados antes da avaliação final. M4 não foi iniciado.

Um subagente implementou o núcleo TF-IDF e os testes em um stage que não continha o arquivo final, a lista de consultas finais ou seus trechos. Outro subagente avaliou Graphify, sem construir grafo. Uma revisão independente usou somente o stage e os dados de desenvolvimento.

### Implementação e evidências

- scikit-learn 1.9.1 fixado no projeto; lockfile registra dependências. Instalação feita em ambiente isolado Python 3.11.17.
- TfidfSearch reutiliza um índice de parágrafos; TF-IDF com stopwords em inglês, demais padrões do scikit-learn e similaridade de cosseno. Filtro, corte, limite de cinco, origem e desempate determinístico preservados.
- CLI mantém busca literal como padrão e acrescenta `--method tfidf`, com score rotulado como cosseno.
- O loader abre somente development.json e confere o hash aprovado, IDs dev-01 a dev-10, tipos e aprovação dos rótulos. Não existe opção de selecionar o conjunto final na calibração.
- Grade de 0 a 1 em passos de 0,1. Regra final: preservar os acertos conhecidos do TF-IDF sem corte; minimizar falsos positivos entre os cortes elegíveis; desempatar pelo menor corte. Resultado min_score = 0,0, sempre excluindo score zero.
- Literal: 3/8 positivas com trecho conhecido no top 5 e 0/2 negativas com retorno. TF-IDF selecionado: 1/8 e 2/2, respectivamente. Esses são resultados de desenvolvimento, com anotações limitadas; não foram apresentados como superioridade ou teste independente.
- A exploração inicial com grade até 0,5 empatou. Ao cobrir todo o intervalo, uma regra de utilidade balanceada favoreceu 0,7, mas perdeu o único acerto conhecido do TF-IDF; adotou-se a preservação de cobertura. Essa revisão usou apenas desenvolvimento e está descrita no relatório metodológico, sem alterar rótulos ou dados.
- A revisão independente encontrou dois riscos: tipos JSON incorretos podiam mudar denominadores, e o caminho de saída podia sobrescrever insumos. Ambos foram corrigidos com regressões; a revisão das correções não encontrou novos achados.
- 48 testes passaram com o corpus real e sem testes ignorados. Incluem cosseno, reuso de índice, OOV/stopwords/entradas vazias, filtros, limites, validação, proteção de insumos e hashes do congelamento.
- O wheel foi instalado em outro ambiente Python 3.11 com dependências exportadas do lockfile; os 48 testes passaram novamente e o relatório reproduzido foi idêntico byte a byte. A configuração TF-IDF está incluída no wheel.

### Aceitação dos gates no M3

| Gate | Evidência |
|---|---|
| Núcleo | Classe TF-IDF e validações cobertas por testes sintéticos; testes escritos antes da implementação. |
| Integração | Desenvolvimento executado sobre os nove TXT do M1, somente com as dez consultas aprovadas. |
| Saídas | Relatório JSON com grade, contagens e IDs; CLI distingue similaridade e ocorrências. Nenhum trecho ou índice foi versionado. |
| Documentação | README e documento TF-IDF apresentam resultados desfavoráveis e limites das anotações. |
| Revisão e build | Revisão independente corrigida, suíte completa, construção do pacote, instalação isolada e conferência do snapshot antes de encerrar. |

O snapshot m3_freeze.json registra hashes do código, configuração, ambiente e rótulos; o conteúdo final não foi carregado nem executado. Para verificar integridade, os arquivos são lidos como bytes opacos, inclusive os rótulos finais. Os originais permanecem fora do Git.

### Graphify — decisão para este tamanho de projeto

Antes do M3 havia cinco módulos Python e 335 linhas, sem grafo existente. A CLI instalada foi verificada como Graphify 0.9.94. A recomendação foi adiar a construção: buscas diretas e os documentos de estado já atendem ao escopo, enquanto um grafo exige criação, revisão de exclusões e atualização. Não foi medido ganho de tokens, custo ou assinatura.

As fontes oficiais descrevem extração estrutural local por AST e extração semântica para documentos: https://github.com/Graphify-Labs/graphify . Se as perguntas repetidas sobre relações crescerem, experimentar apenas código e medir o benefício. Não incluir livros, consultas finais ou documentos que reproduzam as consultas finais durante M3. Nenhuma atualização de skill ou construção de grafo foi realizada.

A avaliação final, a execução do notebook Kaggle e as publicações permanecem pendentes de M4–M6. A comparação de desenvolvimento sugere cautela com a regra de ausência de resposta do TF-IDF; dois exemplos negativos não sustentam generalização.

## Execução do M4 — validação local concluída; Kaggle pendente

Em 25 de outubro de 2026, o usuário aprovou M3 e autorizou preparar o notebook Kaggle, conferir o snapshot e avaliar as vinte consultas finais sem novos ajustes.

O novo avaliador e seus 15 testes sintéticos foram implementados e revisados antes de executar as consultas finais reais. O código M3, o lockfile, a configuração e os rótulos permanecem imutáveis. O avaliador confere os módulos realmente importados e exige Python 3.11.17 e as versões numéricas do snapshot antes de recuperar resultados; usa a função de métricas congelada.

Este commit prepara o código de suporte que será fixado no notebook. As ferramentas Jupyter de validação ficam em um ambiente separado, descrito em notebooks/validation-requirements.txt; não alteram o pyproject ou o lockfile congelados. A primeira execução final e a validação do notebook ocorrerão depois deste registro de suporte.

Não foram encontradas credenciais da API Kaggle no ambiente. A publicação e a execução na conta do autor continuam sendo sua etapa prevista no plano; validação local não será apresentada como execução real no Kaggle.

### Resultado e validação do M4

**Estado:** entrega técnica local pronta, com notebook e avaliação final. O critério de execução/publicação no Kaggle permanece pendente da etapa do autor; não foi declarado como concluído por simulação local. M5–M6 não foram iniciados.

O suporte foi versionado no commit `51a69a0264ef318d8506da0a8db627c295a5ccba` antes da primeira execução real. O notebook fixa esse commit. O código M3, as versões, o corte 0,0, o corpus e os rótulos permaneceram inalterados.

| Método | Positivas com referência conhecida no top 5 | Negativas com retorno indevido |
|---|---:|---:|
| Literal | 7/16 | 0/4 |
| TF-IDF | 8/16 | 4/4 |

Um acerto conhecido adicional do TF-IDF não demonstra superioridade geral, pois o método retornou resultados em todas as negativas. As referências são limitadas e o conjunto é pequeno; não foram alteradas após os resultados.

- 63 testes passaram, sem ignorados, com o corpus real. Os 15 testes novos usam apenas dados sintéticos; a revisão independente não encontrou achados acionáveis no avaliador.
- O avaliador verifica os quinze ativos, os módulos importados e o runtime antes e depois da recuperação e protege insumos contra sobrescrita. Métricas vêm da função congelada do M3.
- O notebook foi validado com nbformat e executado por nbclient em kernel local novo. As sete células de código foram executadas em ordem, sem erro; código e Markdown permaneceram idênticos durante a execução.
- O notebook clonou o commit público de suporte, provisionou Python gerenciado 3.11.17 e sincronizou o lockfile. O relatório ficou idêntico byte a byte ao da primeira avaliação.
- O pacote foi construído e instalado em ambiente separado; 63 testes e reprodução do relatório final passaram também nesse modo.
- Repetições da avaliação tiveram somente finalidade de reprodução; nenhum método, limiar, rótulo ou recorte foi ajustado entre as execuções.
- O relatório versionado e os outputs do notebook contêm metadados, contagens, referências e scores; não incluem corpos dos livros nem caminhos privados da máquina.

O relatório `reports/m4_notebook_validation.json` identifica explicitamente `local_clean_kernel_not_kaggle`. A primeira tentativa de validação e a versão final com visão do corpus passaram; usa-se a evidência da versão final. O registro da configuração M3 continua intacto, inclusive seu indicador histórico de consultas finais ainda não executadas naquele marco.

### Handoff para o autor

Importar `notebooks/sherlock_document_search.ipynb` no Kaggle, anexar o dataset, habilitar Internet, executar todas as células e informar a URL. As instruções completas estão em `docs/kaggle-notebook.md`. Só depois de conferir essa execução será possível registrar o critério hospedado do M4 como validado. Não foi solicitada nem executada publicação automática na conta do autor.


### Reformulação do notebook para o leitor do Kaggle

Após o retorno do autor sobre referências excessivas ao GitHub e falta de visualizações, a apresentação foi reescrita como análise independente: problema de busca documental, acervo, métodos, comparação, erros e limites. A narrativa do notebook não usa nomes de marcos ou instruções internas do repositório.

O código e os metadados necessários estão embutidos em um ZIP determinístico, sem os livros, gerado por `scripts/build_kaggle_bundle.py`. O notebook não clona nem baixa código do projeto; Internet continua necessária para ferramentas, Python gerenciado e dependências quando ausentes do cache. O pacote compartilhado e os quinze ativos M3 foram preservados, sem copiar uma nova implementação da busca para as células.

Foram acrescentados dois gráficos: palavras retidas por obra e comparação dos dois métodos em painéis separados para positivas e negativas. Ambos são exibidos no notebook e exportados em PNG e SVG. As tabelas mostram volume por obra, métricas e as vinte consultas por extenso com os resultados dos métodos. As saídas públicas são `search_results.json` e `figures/` dentro de `/kaggle/working/sherlock_analysis`.

Validação da versão entregue: 65 testes passaram; oito células de código executaram em kernel local limpo, sem erros; dois gráficos inline e quatro arquivos de figura foram conferidos. O relatório reproduzido permaneceu idêntico byte a byte ao original, SHA-256 `92753538b7528cec6332b9415343b313221aae211b4e51fe3ee18a64c8d09324`. Os quinze hashes congelados continuam válidos. Figuras foram inspecionadas visualmente. Uma revisão independente do empacotamento e da interpretação científica não encontrou achados acionáveis.

A nova evidência substitui a validação local anterior em `reports/m4_notebook_validation.json`. A execução e a publicação atuais no Kaggle não foram conferidas por URL; não se concluiu esse critério do M4. M5–M6 não foram iniciados. As figuras são apresentação dos resultados existentes, sem novos ajustes de parâmetros ou rótulos.


## V2 — BM25 e novo conjunto: execução autorizada

O autor autorizou iniciar a v2 em 25 de outubro de 2026, preservando a v1 e seus resultados, registrando o plano e delegando quando benéfico. A extensão segue o [plano v2](docs/v2-plan.md), arquétipo A, sem iniciar M5–M6. A primeira entrega não inclui executar o novo teste nem atribuir aprovação humana aos novos rótulos.

Preservação: tag local `v1-baseline` no commit `8f17985`; branch `codex/search-v2-bm25`; manifesto `evaluation/v2/v1_preservation.json` com SHA-256 de 35 ativos v1 de código, testes, avaliação, relatórios, notebook e ambiente. README e registro de estado podem evoluir; a tag preserva a árvore completa anterior.

O protocolo foi registrado antes das métricas v2: 36 propostas de desenvolvimento (27/9) e 24 reservadas (18/6), fontes de referência em regiões distintas, múltiplas referências conhecidas e separação de intenções. A reserva é procedural, local e ignorada pelo Git. Um curador separado produz o teste sem executar métodos. O implementador não abre suas consultas, rótulos ou trechos.

Núcleo BM25 implementado por subagente com testes antes da implementação. Primeira execução dos testes falhou por ausência do módulo; 16 testes sintéticos passaram após implementar. Sem dependências novas nem alterações nos quinze ativos M3. Comparador de desenvolvimento separado: seus oito testes iniciais também falharam antes de existir o módulo e passaram depois. A revisão independente encontrou desempate vulnerável a arredondamento e evidência de negativas sem tipo estrito; ambos foram corrigidos e acrescentados testes, totalizando onze no comparador. A revisão das correções não encontrou novos achados. O revisor também comparou 300 corpora sintéticos com fórmula independente, sem divergência relevante.

Revisão metodológica anterior às métricas: os curadores inicialmente criaram negativas com premissas refutadas. Essa convenção penalizaria trechos úteis que corrigem a pergunta. As propostas foram reabertas para substituição por detalhes plausíveis não informados, sem usar resultados de busca. A incerteza da anotação permanece explícita e a aprovação humana está pendente.

Estado deste registro de suporte: regras e código preparados antes da primeira comparação real v2; curadoria e execução exploratória de desenvolvimento em andamento. O candidato de corte não altera a configuração distribuída. Nenhuma consulta do teste v2 foi executada.


### V2 — aceite, configuração e congelamento antes do teste

O autor respondeu “aprovado” à solicitação explícita de revisão das 36 consultas de desenvolvimento e 24 reservadas. Alteraram-se exclusivamente os status de revisão; a cópia privada das propostas finais foi preservada. Registrou-se o aceite global do chat, sem afirmar revisão humana individual documentada.

No desenvolvimento aprovado, literal teve 9/27 hits conhecidos e 0/9 negativas com retorno; TF-IDF 10/27 e 9/9; BM25 12/27 e 9/9. A regra pré-registrada produziu corte 32, com 0/27 hits e 3/9 negativas com retorno. Esse candidato foi rejeitado explicitamente por inviabilidade funcional, sem alterar ou ocultar a regra inicial. A decisão anterior ao teste mantém k1=1,2, b=0,75 e min_score=0,0 para avaliar BM25 como ranking, sem resolver abstenção. A análise por tipo está em docs/v2-development.md.

O novo avaliador final e dez testes sintéticos foram implementados antes de abrir semanticamente o teste. Revisão independente confirmou os gates de integridade, aprovação, composição, runtime, fontes importadas e saídas; nenhum achado acionável. Suíte completa com 102 testes passou antes do congelamento. O avaliador não oferece grade, limiar ou seleção de consultas; usa os três métodos fixos. A tag e os 35 ativos v1 permanecem intactos. O freeze v2 registra também a decisão, o desenvolvimento aprovado e o hash do teste local, conferido como bytes opacos nesta etapa.

Este registro e o código serão versionados antes da primeira execução final v2; os resultados ainda não foram calculados neste ponto. A execução subsequente usará exclusivamente o snapshot fixo e não orientará novos ajustes neste ciclo.


### V2 — resultado final e entrega

O suporte foi versionado em `14a0913` antes da primeira execução das 24 finais. O snapshot v2 contém 48 arquivos por hash, incluindo código, ambiente, decisão, desenvolvimento aprovado, fontes v1 e bytes do teste reservado. A execução final usou apenas literal e TF-IDF v1 e BM25 fixo (min_score=0,0), sem grade ou seleção. Depois, o wheel instalado reproduziu o relatório byte a byte, sem alterações.

| Método no mesmo novo teste | Consultas positivas com referência no top 5 | Negativas com retorno |
|---|---:|---:|
| Literal v1 | 6/18 | 0/6 |
| TF-IDF v1 | 10/18 | 6/6 |
| BM25 | 12/18 | 6/6 |

O ganho observado é de recuperação conhecida e ranking no conjunto curado; abstenção não foi resolvida. A média balanceada não favorece BM25 em relação ao literal neste conjunto. Não se apresentou superioridade geral nem desempenho em documentos de clientes. Não houve ajuste após conhecer o teste.

Após concluir, o curador publicou somente metadados em `evaluation/v2/final.json` e uma tabela sem trechos em `docs/v2-final-queries.md`. O JSON público é byte-idêntico ao privado aprovado; este foi mantido junto da proposta original. Os rótulos finais agora são públicos e não podem ser usados como novo teste independente de futuras melhorias. Os estados de não execução dos manifests são históricos do congelamento e permaneceram intactos.

Verificações da entrega: 102 testes passaram no código-fonte e no wheel, com o corpus real e sem testes ignorados; o avaliador foi revisado independentemente antes da execução real; corpus, runtime e fontes importadas conferidos antes/depois; 35 ativos v1 e 15 hashes M3 intactos; 48 arquivos v2 continuam iguais ao freeze. Relatório final SHA-256 `4c05fc86dcd6907bfafec5283b45c5e66ae91aaf3ef323466b54f179039ac92b`. Figuras PNG/SVG geradas do relatório, sem novas buscas, e inspecionadas visualmente. Evidência em `reports/v2/validation.json`.

Os cinco gates de implementação desta extensão foram cumpridos: núcleo testado, integração com corpus e avaliador, figura/JSON inspecionados, documentação de decisões e reprodução, revisão independente e build/instalação. O aceite dos rótulos veio do autor; conclusão técnica não significa aprovação final da entrega pelo autor. A publicação do código continua na branch v2, com a referência v1 preservada.

O notebook Kaggle v1, seus resultados e gráficos foram preservados. Uma integração dos resultados v2 em novo notebook, Quarto ou dashboard ainda não foi executada. A validação ocorreu em Linux local; não se executou a v2 no Kaggle nem em Windows/macOS. Não foram introduzidos embeddings, geração de respostas ou serviços de busca hospedados.


## Notebook Kaggle próprio da v2 e diagnóstico das negativas

O autor aprovou a v2 e autorizou um notebook próprio com três métodos, gráficos e limitações, preservando a v1. Também pediu análise do retorno de TF-IDF e BM25 nas perguntas sem resposta. Condução contínua no arquétipo A; não foi autorizada ou implementada uma v3 de modelos nesta etapa.

Arquivos novos: notebook `notebooks/sherlock_document_search_v2.ipynb`, gerador `scripts/build_kaggle_v2_bundle.py`, validador `scripts/validate_notebook_v2.py`, quatro testes de bundle, documentação de importação e diagnóstico. O builder incorpora 51 entradas: 48 ativos congelados, freeze, README mínimo e relatório de referência. Usa a cópia pública das consultas para restaurar o caminho esperado pelo avaliador; nenhum TXT ou documento local com trechos é incluído. V1, seus auxiliares e os 48 arquivos v2 permanecem inalterados.

Os testes do builder falharam inicialmente pela ausência do módulo e passaram após implementação. Cobrem determinismo, hashes, correspondência com o payload real do notebook, proteção de caminhos, reprodução sem o holdout local e escrita exclusiva no notebook v2. A suíte completa passou com 106 testes, incluindo dados reais e sem ignorados. Revisão independente do notebook, bundle e limites científicos não encontrou achados acionáveis.

O notebook executou oito células em kernel local novo, sem erro; gerou duas figuras inline e quatro arquivos PNG/SVG. Seu relatório reproduziu byte a byte o final aprovado, SHA-256 `4c05fc86dcd6907bfafec5283b45c5e66ae91aaf3ef323466b54f179039ac92b`. Os gráficos foram inspecionados visualmente. A única mudança posterior de metadata recolhe a célula do payload; fontes e outputs foram preservados. Evidência própria em `reports/v2/notebook_validation.json`; figuras em `reports/v2/notebook_figures/`. O notebook v1 continua byte-idêntico e os verificadores confirmam 35 ativos v1 e 48 v2.

O diagnóstico foi delegado a modelo mais leve: leitura de fontes, resultados pré-computados e inspeção descritiva dos seis top 1s. Não foram feitos fit, novas buscas, grades ou mudanças de rótulos/modelos. Palavras compartilhadas geram scores positivos com corte zero mesmo sem evidência do atributo; o relatório distingue busca de textos relacionados de suficiência de evidência. Propõe rótulos de pares pergunta–trecho e decisão de abstenção em outro desenvolvimento/teste, sem declarar melhoria já validada. Os testes finais v1/v2 já foram vistos e não são independentes para escolher uma próxima configuração.

Gates: integração por reprodução congelada, figuras e tabelas verificadas, documentação de execução e limites, testes e revisão independente concluídos. A entrega local foi validada; execução ou publicação real da v2 no Kaggle não foi conferida. O autor fará a importação na plataforma conforme o fluxo já acordado. Quarto, dashboard e novos modelos não foram iniciados.


## Consolidação da apresentação e preparação do PR v2 → main

Em 25 de outubro de 2026, o autor aprovou reorganizar o README e preparar o PR da v2 para main, preservando os dois notebooks, resultados e arquivos congelados. A autorização cobre commit, publicação da branch e abertura do PR; não inclui executar o merge ou iniciar Quarto, dashboard ou novos modelos.

O README foi reorganizado como entrada única do projeto: problema e três métodos, notebook v2 como ponto de entrada, comparação no mesmo teste v2, execução local e verificação, dados/proveniência e histórico separado da v1. A cronologia detalhada continua nos documentos existentes. O histórico identifica tamanhos e métodos dos conjuntos, sem combinar métricas de avaliações diferentes. O notebook v1 e seus resultados seguem acessíveis por seus caminhos originais e pela tag v1-baseline.

A primeira redação foi delegada a modelo mais leve e revisada pelo agente principal, com conferência dos números, denominadores, comandos e links locais. A revisão substituiu a tabela histórica de scores por uma identificação explícita dos conjuntos, eliminando a possibilidade de confundir resultados de testes distintos. Não foram criados testes artificiais para a alteração documental.

Verificações desta preparação: 106 testes passaram novamente com o corpus real, sem ignorados; os verificadores confirmaram os 35 ativos v1 e 48 arquivos do congelamento v2; os dois notebooks conferem com seus hashes de validação; os payloads dos dois notebooks conferiram antes da publicação. A comparação remota identificou main em 8f17985 e v2 cinco commits à frente antes desta edição, sem divergência; não havia PR aberto dessa branch para main na consulta realizada.

O PR integra a branch completa codex/search-v2-bm25 em main: BM25, avaliação v2, notebook próprio, diagnóstico e documentação consolidada. A descrição registra validação local e limitações, sem alegar CI ou execução real no Kaggle. O merge fica pendente de autorização específica. Nenhum arquivo além de README.md e deste registro foi alterado nesta consolidação.


## Merge do PR #1 e M5 — relatório Quarto para Pages

O autor aprovou explicitamente o merge preservando histórico e autorizou iniciar o M5 em 25 de outubro de 2026. O merge foi feito pela API com método `merge` e SHA esperado `36be9d7`; resultado `95fda2e7a02cf2b3b03c55686ac533a7fa861a8e`, pais `8f17985` e `36be9d7`. A main local foi atualizada por fast-forward, sem reescrever os commits anteriores. O M5 foi preparado na branch `codex/m5-quarto-report`.

Escopo do M5 conforme o plano aprovado: autoria/renderização HTML e publicação verificada no GitHub Pages do mesmo repositório público. Notebook Kaggle, modelos, rótulos, resultados e snapshots permanecem preservados; M6 não foi iniciado. A autorização do M5 cobre esta publicação do relatório no destino nomeado, sem introduzir outro serviço ou alterar acesso ao código/dados já públicos.

O Quarto 1.10.19 já estava instalado e a versão oficial foi confirmada. O ambiente Jupyter dos modelos não foi alterado; foi criado ambiente de relatório Python 3.11.17, com ferramentas próprias e PyYAML. O diagnóstico inicial de Quarto apontou PyYAML ausente no ambiente antigo; o ambiente separado resolveu essa dependência e a renderização efetiva passou.

Fontes em site/index.qmd, configuração/style/assets em site/, helpers stdlib de fontes/render/HTML em scripts/, testes próprios em tests/. O conteúdo inicial foi delegado, verificado contra JSONs e revisado para que a figura de corpus descrevesse somente palavras retidas. O checker independente encontrou falta de alt explícito e uma referência histórica; ambos corrigidos antes da publicação. O relatório executa cinco células de leitura/formatação, sem importação de métodos de busca, fit ou varreduras. Os 50 hashes verificados incluem o snapshot original e a referência final; o metadado antes privado é obtido da cópia pública idêntica.

Validação local: 115 testes passaram com os dados reais e sem ignorados; nove são novos testes de fontes/HTML. Quatro tabelas, duas imagens com alt e seis referências cruzadas conferem com as fontes; 30 links/recursos locais e cinco CSS verificados. Render HTML inspecionado no navegador. Fontes remotas desnecessárias foram retiradas do tema, preservando fontes de sistema. As verificações dos 35 ativos v1, 48 arquivos v2 e ambos payloads de notebooks passaram.

O workflow foi revisado independentemente: build sem permissão de deploy em PR, artifact publicado somente a partir de main, deploy dependente do build validado e permissões mínimas. Pages não estava configurado (GET 404); gh confirmou administração do repositório, Actions habilitado e destino público. A configuração de Pages, execução remota e smoke tests serão registrados em evidência própria após a publicação; validação local não os substitui.


### M5 — publicação concluída e verificada

A configuração inicial de Pages foi criada com `build_type: workflow`. A implementação `b55ff7027641d3e4421cc95ca919f9c6626070a1` foi integrada à main por fast-forward e publicada. O [run 40256849352](https://github.com/talesgomes27/sherlock-document-search/actions/runs/40256849352) concluiu build e deploy com sucesso; o build remoto executou os nove testes do relatório e renderizou as cinco células.

O [relatório público](https://talesgomes27.github.io/sherlock-document-search/) respondeu HTTP 200. A metadata publicada confirma o commit b55ff70 e árvore limpa, Python 3.11.17 e Quarto 1.10.19. O smoke test baixou os 21 arquivos do artifact e conferiu seus hashes, os 50 hashes de entrada e as quatro tabelas, duas imagens, seis referências cruzadas e 30 links/recursos locais. A página pública também foi inspecionada visualmente no navegador. Evidência em `reports/m5/publication_validation.json` e `reports/m5/publication.png`.

Os 35 ativos v1, os 48 arquivos congelados v2 e os dois notebooks continuam preservados. Não houve nova avaliação ou ajuste de modelos. O commit subsequente contém somente documentação e evidência, sem novo deploy; o commit-fonte publicado continua b55ff70. M5 tecnicamente concluído; aprovação de apresentação pelo autor continua distinta desta verificação. M6 e execução real no Kaggle permanecem pendentes.


## Revisão editorial e visualização por consulta

O autor pediu linguagem moderada entre técnica e não técnica no relatório Quarto, notebooks Kaggle e README e perguntou sobre novas visualizações. A skill humanizer orientou a revisão: explicar medidas antes do jargão, retirar repetição e manter números, protocolo e limitações. Um subagente mais econômico redigiu README e textos dos notebooks/Quarto; outro analisou a utilidade da matriz e fez revisão independente. O agente principal conferiu e integrou as propostas.

A revisão foi preparada em `codex/editorial-humanization`. Para preservar hashes e validações históricas, os notebooks originais continuam intactos; as edições para leitura e importação no Kaggle estão em `notebooks/portfolio/`, com links no README, relatório e documentação. Todas as oito células originais de código de cada notebook, inclusive payload, saídas e metadados, são idênticas às originais. Mudaram apenas textos Markdown, além da inclusão de uma célula de visualização em cada cópia.

A matriz mostra a posição da primeira referência conhecida por consulta positiva, usando apenas os JSONs já publicados. × indica referência conhecida ausente no top 5, sem julgar todos os demais trechos. O README e o Quarto usam a matriz v2; cada notebook contém a matriz de seu próprio teste. Não se combinaram avaliações v1/v2. A revisão independente levou a explicitar a insensibilidade a maiúsculas da busca literal e a descrever o ganho como MRR@5 maior, evitando sugerir melhora uniforme. Não houve mudança de parâmetros, rótulos ou resultados finais.

Validação: 118 testes locais passaram, sem ignorados; 12 testes específicos de fontes/HTML/posições/preservação ficam no fluxo do relatório. As cinco células do Quarto e os comandos do README permanecem byte-idênticos. Render com três imagens, quatro tabelas, sete referências cruzadas e 32 links/recursos locais conferidos. As duas novas células de gráfico executaram isoladamente com resultados salvos; as cópias completas não foram reexecutadas e o Kaggle permanece sem verificação. Os 35 ativos v1, 48 arquivos do snapshot v2 e os dois notebooks originais continuam íntegros. Evidência e captura em `reports/editorial/`; escopo documentado em `docs/editorial-presentation.md`.

A revisão é entregue em PR para revisão do autor. A página pública continua na versão aprovada do M5 até o merge; não se iniciou M6 ou nova versão de modelos.
