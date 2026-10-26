# V2 — BM25 e nova avaliação

## Autorização e estado

O autor autorizou iniciar a v2 no chat em 25 de outubro de 2026, registrando o plano e usando subagentes quando benéfico. Arquétipo A, Python, condução contínua dentro deste escopo. A v1 corresponde ao commit `8f17985`: seu notebook, fontes congeladas, dependências, rótulos e resultados serão preservados. M5–M6 e publicação no Kaggle não fazem parte desta extensão.

A primeira entrega inclui implementação BM25, propostas de desenvolvimento e teste reservado, comparação exploratória de desenvolvimento e documentação. A revisão dos novos rótulos e a avaliação final da v2 são gates posteriores; não se atribuirá aprovação humana a propostas geradas por agentes.

## Hipótese e escopo

Testar se BM25 melhora a recuperação de referências conhecidas com custo local pequeno. Comparar separadamente o efeito de recusar resultados abaixo de um corte. Nenhum ganho é garantido. Manter corpus, parágrafos, top 5, filtro por arquivo e referências de linhas da v1. Começar com BM25 fixo em k1=1,2 e b=0,75, sem busca de hiperparâmetros e sem novas dependências. Embeddings, reranking e mudança de segmentação ficam fora desta primeira rodada.

A implementação usa a biblioteca numérica já congelada, CountVectorizer com stopwords em inglês e seus padrões de tokenização. Para cada termo distinto da consulta: IDF = log(1 + (N - df + 0,5)/(df + 0,5)); contribuição = IDF × tf × (k1 + 1)/(tf + k1 × (1 - b + b × dl/avgdl)). N inclui todos os parágrafos; dl conta tokens após a mesma análise textual. Essa fórmula é inspirada no BM25 Okapi, não uma reprodução bit a bit do Lucene. Scores não são probabilidades e não são comparáveis aos scores TF-IDF.

Fonte primária: [BM25Similarity, Lucene](https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/search/similarities/BM25Similarity.html).

## Novo conjunto e separação

- Desenvolvimento: 36 propostas, 27 positivas (9 exatas, 9 paráfrases, 9 de contexto) e 9 negativas plausíveis; três positivas por obra.
- Teste reservado: 24 propostas, 18 positivas (6 de cada tipo) e 6 negativas plausíveis; duas positivas por obra. Criado por subagente separado, sem executar métodos de busca.
- Referências positivas de desenvolvimento vêm da faixa de 20–45% do corpo de cada obra; as de teste, da faixa de 60–85%. Isso reduz sobreposição de passagens, mas não prova independência sem revisão de intenção e conteúdo.
- Excluir repetições e paráfrases das trinta perguntas antigas e entre os dois novos grupos. Conferir fatos e múltiplas referências conhecidas antes da execução. Referências são limitadas, sem supor completude dos julgamentos.
- Negativas perguntam detalhes plausíveis não informados de eventos reais. Perguntas com premissa explicitamente refutada têm uma fonte útil de correção e não serão negativas automaticamente. A primeira proposta usava essa convenção inadequada e foi substituída antes de qualquer métrica. Negativas devem ter justificativa e evidência de verificação; ausência de uma palavra isolada não prova ausência de resposta. Casos incertos continuam como propostas, nunca como verdade aprovada.
- O teste fica em `data/processed/v2_holdout/`, ignorado pelo Git; somente contagens e hashes são publicados em `evaluation/v2/holdout_manifest.json`. O implementador não abre perguntas, rótulos ou trechos desse diretório. O subagente responsável verifica duplicação com o desenvolvimento e relata somente metadados.
- Essa reserva é uma separação de procedimento, não um controle criptográfico de acesso. O autor pode revisar os arquivos locais e pedir correções ao revisor sem transmitir seu conteúdo ao implementador.
- As vinte finais da v1 já foram vistas: são resultado histórico e podem informar hipóteses, mas não serão usadas para escolher configurações nem apresentadas como teste independente da v2.

## Critérios e métricas definidos antes dos experimentos

Relatar hit de referência conhecida no top 5, posição da primeira referência nas positivas (MRR@5), negativas com algum retorno e positivas sem retorno. As referências são não exaustivas: não chamar hit conhecido de precisão ou recall completo. Nas perguntas de contexto, recuperar uma referência conhecida não garante evidência completa para todas as partes da pergunta. Latência será uma medição local descritiva, separando construção do índice e consultas, sem promessa de serviço.

BM25 sem corte é o novo comparador. Examinar também cortes absolutos pré-definidos: 0; 0,5; 1; 2; 4; 8; 16; 32. O candidato maximiza a média de hit conhecido e abstenção nas negativas; desempates favorecem menor taxa de retorno nas negativas e, depois, menor corte. Essa regra explicita que pode perder acertos para reduzir retornos indevidos. Resultados sobre rótulos propostos são exploratórios; o candidato não é aplicado à configuração distribuída nem congelado como versão final.

Somente após revisar desenvolvimento e escolher a configuração, congelar os arquivos da v2. Em seguida, executar literal e TF-IDF da v1 e BM25 da v2 no mesmo novo teste reservado. Não comparar diretamente percentuais calculados em conjuntos diferentes. Consultar esse teste para escolher novos ajustes exige outro ciclo independente.

## Tarefas e aceitação

1. Preservar v1: tag de referência e manifesto dos ativos versionados; verificar os quinze hashes M3 e o relatório M4, sem modificar seus arquivos.
2. BM25: módulo novo e CLI separada, testes de fórmula calculada independentemente, ranking, OOV, filtros, limites, entradas inválidas, não mutação e reuso do índice. Não alterar módulos congelados.
3. Consultas: produzir os dois grupos, validar IDs/referências/faixas e revisão de fatos. Status inicial `proposed`; revisão humana pendente. Livros e trechos permanecem fora do Git.
4. Desenvolvimento: módulo que lê exclusivamente `evaluation/v2/development.json`; rótulos não aprovados exigem opção explícita de exploração. Relatório novo, sem tocar em saídas v1. Testes sintéticos e execução local sobre corpus real.
5. Revisão e entrega inicial: revisão independente, suíte, build e CLI do pacote instalado; evidências em `task.md`. Preparar instruções de revisão e não executar o teste reservado.
6. Etapa posterior: aceite dos rótulos, calibração confirmada, congelamento v2 e execução do novo teste. Notebook e gráficos v1 continuam históricos; a integração dos novos resultados só ocorrerá depois desta etapa.
