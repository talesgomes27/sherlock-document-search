# M3 — TF-IDF e comparação de desenvolvimento

O M3 acrescenta busca por TF-IDF e similaridade de cosseno, preservando os mesmos parágrafos e referências do M1. Os ajustes usam somente as dez consultas de desenvolvimento aprovadas. Nenhuma consulta final foi carregada ou executada neste marco.

## Executar

Na raiz do projeto:

```bash
uv sync --python 3.11 --frozen
uv run python -m sherlock_search --method tfidf --query "Cyanea" --book the_case-book_of_sherlock_holmes.txt
uv run python -m sherlock_search.development --output data/processed/m3_reproduced.json
uv run python -m sherlock_search.development --check-freeze
```

O primeiro comando instala as versões do lockfile. A consulta retorna até cinco parágrafos ou informa ausência de correspondência. O terceiro comando reproduz apenas o desenvolvimento e grava um relatório separado; não altera a configuração distribuída. A verificação do congelamento compara hashes, inclusive dos arquivos de rótulos como bytes opacos, sem interpretar ou executar consultas finais.

A CLI mantém a busca literal como padrão. `--method tfidf` exige `--query`; o filtro `--book` recebe o nome exato do TXT. A rotina de comparação recusa gravar resultados dentro das pastas de consultas ou dados brutos, protegendo os insumos. Para usar os TXT diretamente em `data/`, informe `--raw-dir data` e mantenha a saída em `reports/`, fora dessa pasta de insumos.

## Núcleo e parâmetros

```python
from pathlib import Path
from sherlock_search.corpus import prepare_corpus
from sherlock_search.tfidf import TfidfSearch

paragraphs, _ = prepare_corpus(Path("data/raw"))
index = TfidfSearch(paragraphs)
results = index.search("Cyanea", filename="the_case-book_of_sherlock_holmes.txt")
```

O índice é ajustado uma vez no corpus inteiro e reutilizado nas consultas. O filtro não refaz o vocabulário. Usa-se `TfidfVectorizer(stop_words="english")`, com os demais padrões do scikit-learn 1.9.1: palavras/unigramas, normalização L2 e IDF suavizado. A similaridade é calculada com `cosine_similarity`.

Fontes técnicas: [TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html) e [cosine_similarity](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html).

`score` é um número de similaridade de cosseno, não uma probabilidade de correção. Resultados são cópias dos parágrafos originais; texto, ID, obra e linhas são preservados. Aplicam-se o filtro e o corte antes do limite de cinco. Empates usam arquivo e linhas. Corpus vazio, vocabulário vazio e consultas vazias, só com stopwords/pontuação ou fora do vocabulário retornam uma lista vazia.

A regra distribuída está em `tfidf_config.json`: **min_score = 0,0**, exigindo também `score > 0`. Um argumento explícito no construtor é permitido para os experimentos de desenvolvimento; a execução normal usa o valor congelado.

## Escolha do corte

A comparação registra uma grade de 0,0 a 1,0, em passos de 0,1. A regra final preserva os acertos conhecidos do TF-IDF sem corte adicional; entre os candidatos que preservam essa cobertura, minimiza os retornos nas negativas. Empates preferem o menor corte.

Durante a exploração somente em desenvolvimento, uma grade inicial de 0,0 a 0,5 não diferenciou os resultados. Ampliou-se a grade para todo o intervalo. Uma regra inicial baseada na média entre recuperação conhecida e abstenção favoreceu 0,7, mas esse corte perdeu o único acerto conhecido do TF-IDF. Essa regra foi descartada em favor da preservação de cobertura, e a decisão ficou em 0,0. Não foram alterados consultas, rótulos, parágrafos ou referências para melhorar os números.

Nos cortes testados, não houve ponto que reduzisse os falsos positivos sem perder esse acerto. Isso limita o método; a regra não identifica semanticamente todas as perguntas sem resposta.

## Resultado observado — desenvolvimento

| Método | Consultas positivas com trecho conhecido no top 5 | Consultas negativas com retorno indevido |
|---|---:|---:|
| Literal | 3/8 (37,5%) | 0/2 (0%) |
| TF-IDF com corte selecionado | 1/8 (12,5%) | 2/2 (100%) |

O relatório [m3_development.json](../reports/m3_development.json) inclui a grade completa, IDs retornados, contagens, regra de seleção e versões. Os números são de desenvolvimento, usado para escolher a regra; não são resultados independentes de teste final.

Os rótulos contêm trechos relevantes conhecidos, sem pretensão de exaustividade. Não recuperar o ID anotado não prova que todos os outros resultados sejam irrelevantes. O conjunto também é pequeno e curado, com negativas anacrônicas. Não há evidência, neste experimento, de que o TF-IDF supere a busca literal ou resolva a ausência semântica de resposta.

## Congelamento antes do M4

O arquivo [m3_freeze.json](../evaluation/m3_freeze.json) registra os hashes do código de recuperação/preparação, configuração, manifests, dependências, rótulos aprovados e relatório de desenvolvimento. Os TXT continuam identificados por seus hashes no manifesto original e fora do Git; nenhum índice persistente foi versionado.

Antes de executar a avaliação final no M4, conferir esse snapshot e reproduzir o ambiente do lockfile. O verificador lê arquivos de rótulos apenas para comparar bytes. Mudanças posteriores em algoritmo, regra, rótulos ou corpus precisam de registro e revisão; resultados finais não devem orientar novos ajustes apresentados como validação independente.

O M3 inclui testes sintéticos de ranking/cosseno e seus limites, validação dos dados de desenvolvimento, proteção de arquivos e congelamento. O notebook Kaggle, a avaliação das vinte consultas finais e as publicações continuam reservados aos marcos seguintes.
