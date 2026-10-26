# Sherlock Document Search

Projeto de portfólio em Python para encontrar referências em um acervo de documentos. Cada resultado indica a obra, o arquivo de origem e as linhas do parágrafo encontrado. O exemplo usa textos em inglês de Sherlock Holmes; a interface e a documentação estão em português.

O projeto busca nos mesmos parágrafos de três maneiras:

- **Literal**: procura a palavra ou expressão inteira, sem distinguir maiúsculas de minúsculas.
- **TF-IDF**: ordena passagens pela semelhança entre as palavras da consulta e as do texto, usando uma medida chamada similaridade de cosseno.
- **BM25**: também compara palavras, mas leva em conta a frequência delas e o tamanho do texto.

As pontuações de similaridade de cosseno e BM25 não são probabilidades de a resposta estar correta. TF-IDF e BM25 podem encontrar passagens com palavras em comum com a consulta sem trazer o detalhe pedido.

## Leia o relatório

[Relatório Quarto no GitHub Pages](https://talesgomes27.github.io/sherlock-document-search/) · [Fontes e reprodução do relatório](docs/quarto-report.md)

O relatório apresenta os dados, os métodos e os resultados. Também analisa consultas sem resposta e registra o histórico da v1. As tabelas são calculadas a partir dos JSONs aprovados. A página publicada não executa as buscas nem ajusta modelos.

## Experimente no Kaggle

[Abra o notebook v2](notebooks/portfolio/sherlock_document_search_v2.ipynb), importe-o como um notebook novo, anexe o [dataset Sherlock Holmes Series](https://www.kaggle.com/datasets/talesgomes27/sherleck-books), habilite Internet e execute todas as células. O notebook já contém o código necessário, então não é preciso clonar o repositório. Os textos anexados são os dados de entrada. A execução no Kaggle ainda não foi verificada.

O notebook apresenta os três métodos e os resultados de 18 perguntas com referências conhecidas (consultas positivas) e seis sem resposta no contexto examinado (negativas). Cada retorno indica suas linhas de origem. Top 5 significa os cinco primeiros resultados. O gráfico abaixo resume o teste cuja configuração foi fixada antes da avaliação.

![Comparação dos três métodos no mesmo teste v2](reports/v2/figures/final_comparison.png)

| Método | Positivas com referência conhecida no top 5 | Negativas com retorno (falsos positivos neste teste) |
|---|---:|---:|
| Literal | 6/18 | 0/6 |
| TF-IDF | 10/18 | 6/6 |
| BM25 | 12/18 | 6/6 |

A lista de referências conhecidas não é completa, e um resultado pode servir como evidência parcial. Neste conjunto, BM25 encontrou referências conhecidas em mais consultas positivas que TF-IDF. Os dois métodos também retornaram passagens para as seis consultas sem resposta. O teste não demonstra que um método seja melhor em geral nem que consiga reconhecer com confiança quando não há resposta. Como os conjuntos de avaliação v1 e v2 têm tamanhos diferentes, seus percentuais não devem ser somados nem comparados diretamente.

A matriz abaixo mostra as diferenças entre perguntas. Os números indicam a posição da primeira referência conhecida; × significa que ela não apareceu nos cinco primeiros resultados. Cinco consultas ficaram sem referência conhecida recuperada pelos três métodos. A matriz também mostra uma consulta em que TF-IDF encontrou a referência e BM25 não.

![Posição da primeira referência conhecida por consulta positiva da v2; números de 1 a 5 e × para referência ausente no top 5](site/assets/query_positions.png)

As [edições de apresentação](docs/editorial-presentation.md) dos notebooks têm linguagem revisada e uma matriz do respectivo teste. O código e as saídas originais do processamento foram mantidos; os notebooks validados continuam nos caminhos históricos.

## Executar localmente

É necessário ter Python 3.11.17 e [uv](https://docs.astral.sh/uv/). Na raiz do repositório, execute:

```bash
uv sync --managed-python --python 3.11.17 --frozen
uv run python -m sherlock_search --download
```

Use `--download` apenas para obter os dados pela primeira vez. Se os nove TXT já estiverem em `data/raw/`, pule esse comando. O download confere os hashes e não sobrescreve uma pasta existente. O corpus não é armazenado no Git. A preparação separa o material em parágrafos e mantém as linhas do TXT original para que cada trecho possa ser localizado.

Exemplos de consulta:

```bash
uv run python -m sherlock_search --query "Cyanea"
uv run python -m sherlock_search --method tfidf --query "Cyanea"
uv run python -m sherlock_search.bm25 --query "Trichinopoly cigar"
```

Cada comando exibe o resultado, a obra, o arquivo e o intervalo de linhas de origem. A busca literal exige que o texto coincida exatamente; os outros métodos ordenam passagens que compartilham palavras com a consulta. [Preparação e comandos](docs/data-preparation.md) · [Reprodução da avaliação v2](docs/v2-final-evaluation.md).

Depois de preparar os dados, execute a suíte:

```bash
uv run python -m unittest discover -s tests -q
```

A suíte contém 118 testes, incluindo testes de integração com os dados reais. Se os TXT não estiverem disponíveis, os testes que dependem do corpus real são ignorados. Nesse caso, a execução não verifica a integração com os dados reais.

## Dados e proveniência

O corpus verificado contém **9 TXT**, **4.041.127 bytes**, **15.598 parágrafos** e **656.884 palavras retidas**. Os recortes editoriais excluíram 29.566 palavras. Cada parágrafo mantém o nome do arquivo e as linhas de origem. A fonte publicada é o [dataset no Kaggle](https://www.kaggle.com/datasets/talesgomes27/sherleck-books). [Detalhes de proveniência e pendências sobre publicação de trechos](docs/provenance.md). Os arquivos do corpus não ficam no Git.

## Histórico dos testes

A v1 está preservada na tag `v1-baseline` e no notebook original. A v2 inclui BM25 em um notebook próprio; os arquivos históricos continuam nos caminhos originais.

| Experimento | Métodos | Consultas de desenvolvimento | Consultas finais |
|---|---|---:|---:|
| v1 | Literal, TF-IDF | 10 (8 positivas + 2 negativas) | 20 (16 positivas + 4 negativas) |
| v2 | Literal, TF-IDF, BM25 | 36 (27 positivas + 9 negativas) | 24 (18 positivas + 6 negativas) |

- [Notebook v1 para leitura e Kaggle](notebooks/portfolio/sherlock_document_search_v1.ipynb) · [Notebook v1 preservado](notebooks/sherlock_document_search.ipynb) · [relatório v1](reports/m4_final.json)
- [Plano e desenvolvimento v2](docs/v2-plan.md) · [resultados de desenvolvimento](docs/v2-development.md)
- [Avaliação final v2 e reprodução](docs/v2-final-evaluation.md) · [diagnóstico das seis negativas](docs/v2-no-answer-analysis.md)

## Próximas etapas e limites

A v2 e seus resultados foram validados localmente. O relatório Quarto do M5 reúne a análise no GitHub Pages. O dashboard Streamlit (M6) está planejado, mas ainda não foi iniciado. A avaliação em literatura não mede o desempenho em documentos de clientes. O portfólio demonstra preparação de texto, recuperação de informação, avaliação e comunicação analítica.

## Documentação e artefatos

- [Instruções e validação do notebook Kaggle v2](docs/kaggle-notebook-v2.md)
- [Consultas e protocolo v1](docs/queries.md) · [revisão v1](docs/query-review.md)
- [Consultas finais v2](docs/v2-final-queries.md) · [desenvolvimento v2](evaluation/v2/development.json)
- [Relatório numérico da preparação](reports/m1_quality.json) · [manifesto do corpus](src/sherlock_search/corpus_manifest.json)
- [Busca literal e limites](docs/literal-search.md) · [TF-IDF e limites](docs/tfidf-search.md)
- [Planos geral](docs/plan.md) e [v2](docs/v2-plan.md) · [glossário inicial](GLOSSARY.md) · [registro de execução](task.md)

## English summary

Sherlock Document Search is a Python portfolio project for finding traceable references in the Sherlock Holmes corpus. It compares literal search, TF-IDF, and BM25; each result includes its source file and line range. In the v2 test, the methods found known references in 6/18, 10/18, and 12/18 positive queries, respectively. TF-IDF and BM25 returned results for all six negative queries. These results do not establish general superiority or performance on business documents; hosted Kaggle execution remains unverified. The v2 notebook includes its code for Kaggle and uses the attached dataset.
