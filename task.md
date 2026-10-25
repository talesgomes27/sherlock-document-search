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
