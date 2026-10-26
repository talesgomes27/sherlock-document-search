# Edições para leitura e Kaggle

O README, o relatório Quarto e os textos dos notebooks foram revistos para leitores que conhecem análise de dados em níveis diferentes. As explicações apresentam primeiro o que cada medida conta e depois o nome técnico. Números, parâmetros, consultas e limitações dos experimentos continuam os mesmos.

## Qual notebook usar

- [V2: literal, TF-IDF e BM25](../notebooks/portfolio/sherlock_document_search_v2.ipynb), recomendada para conhecer o projeto e importar no Kaggle.
- [V1: literal e TF-IDF](../notebooks/portfolio/sherlock_document_search_v1.ipynb), para acompanhar o primeiro experimento.

Cada arquivo inclui o código necessário; no Kaggle, anexe o dataset, habilite Internet e execute as células na ordem. Não precisa buscar código no GitHub. As instruções e pastas de saída continuam nas próprias células.

Os [originais v1](../notebooks/sherlock_document_search.ipynb) e [v2](../notebooks/sherlock_document_search_v2.ipynb) permanecem nos caminhos usados pelas validações históricas. A cópia editorial muda a explicação e acrescenta uma célula de visualização. Todas as oito células originais de código de cada notebook, incluindo código embutido, saídas, metadados e contadores de execução, foram preservadas integralmente. Os arquivos congelados não foram reescritos para acomodar a revisão de linguagem.

## O que a nova matriz mostra

Cada linha é uma consulta positiva do respectivo teste, e cada coluna é um método. O número informa a posição da primeira referência conhecida entre os cinco resultados; × indica que ela não apareceu ali. Outros trechos podem ser relevantes, e uma referência conhecida pode fornecer evidência parcial. As negativas continuam nas tabelas e nos gráficos de resumo: não entram na matriz de posições.

Na v2, a matriz torna visíveis as cinco consultas sem referência conhecida recuperada pelos três métodos e a perda do BM25 na consulta 08. Os testes conferem que as posições reproduzem os totais publicados e, para a v2, o MRR@5. A figura lê apenas o relatório salvo; não realiza busca ou escolha de parâmetros.

O relatório Quarto e o README usam a matriz da v2. Os dois notebooks contêm a matriz de seu próprio teste; as taxas de v1 e v2 não são comparadas diretamente. A PNG e a SVG do Quarto estão em `site/assets/query_positions.*`. Para regenerá-las em um ambiente com Matplotlib, use:

```bash
python scripts/plot_query_positions.py reports/v2/final.json site/assets/query_positions.png
```

Um gráfico separado de MRR repetiria parte da informação de posições; mais barras com os mesmos totais também acrescentariam pouco. Comparações de velocidade, intervalos de confiança ou gráficos de calibração exigiriam medições ou hipóteses adicionais e não foram criados nesta revisão.

## O que foi verificado

A [evidência dos notebooks](../reports/editorial/notebook_validation.json) registra os hashes das cópias e dos originais. As células novas foram executadas isoladamente em kernel local com os JSONs aprovados. As saídas antigas foram reaproveitadas dos notebooks validados; esta revisão não é uma nova execução integral de cada notebook. A execução no Kaggle permanece sem verificação, e a atualização na plataforma fica com o autor.

A revisão não recalcula a avaliação final para decidir alterações de modelos. Os conjuntos finais já publicados continuam disponíveis para reprodução e diagnóstico; outro ajuste exigiria um novo teste independente.


## Publicação aprovada

O autor aprovou o [PR #2](https://github.com/talesgomes27/sherlock-document-search/pull/2), integrado por merge commit `235fc36` com histórico preservado. O [relatório revisado está publicado](https://talesgomes27.github.io/sherlock-document-search/); build e deploy concluíram no [run 40258089685](https://github.com/talesgomes27/sherlock-document-search/actions/runs/40258089685). A verificação do destino conferiu a identidade do commit, os hashes dos 23 arquivos publicados e as quatro tabelas. A linguagem revisada e os três gráficos foram inspecionados no navegador.

A [evidência de publicação](../reports/m5/pr2_publication_validation.json) complementa a validação editorial inicial, cujo estado de prévia registra o momento anterior ao aceite. Os quatro notebooks conferem com os hashes registrados; esta publicação não equivale a uma execução deles no Kaggle.
