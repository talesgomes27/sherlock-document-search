# Sherlock Document Search

Projeto Python de busca documental e análise exploratória do acervo Sherlock Holmes. O **M1 — dados e preparação** foi aprovado. O **M3 — TF-IDF e desenvolvimento** está concluído, após o aceite do M2 e das 30 consultas. A avaliação final do M4 e o notebook reformulado foram validados localmente, com gráficos e tabelas. A execução atual no Kaggle ainda não foi conferida; relatório Quarto e dashboard Streamlit ficam para M5–M6.

O objetivo é demonstrar competências aplicáveis a serviços freelancer: preparação de textos, recuperação de informação, avaliação de resultados e comunicação analítica. O exemplo é voltado a pequenas equipes que precisam localizar informações em acervos documentais. Resultados no corpus literário não comprovam desempenho em documentos de clientes nem retorno comercial.

## Executar o M1

Com Python 3.11 ou superior e uv, na raiz do repositório:

```bash
uv sync --python 3.11
uv run python -m sherlock_search --download
uv run python -m unittest discover -s tests -v
```

A preparação usa a biblioteca padrão; a busca TF-IDF usa scikit-learn 1.9.1 e suas dependências, registradas no lockfile. O download cria `data/raw/` e recusa sobrescrever uma pasta existente; para reutilizar os TXT e gerar novamente as saídas, execute `uv run python -m sherlock_search` sem `--download`.

Saídas locais: `data/processed/paragraphs.jsonl`, com texto e linhas de origem, e `data/processed/quality.json`, com metadados e contagens. Os originais e os parágrafos preparados ficam fora do Git. A instalação inicial e o download exigem rede; a preparação de dados já disponíveis pode executar sem rede.

## Resultado do M1

- **9 arquivos verificados**, 4.041.127 bytes.
- **15.598 parágrafos**, cada um com título da obra, nome do arquivo e intervalo de linhas de origem.
- **656.884 palavras retidas**; 29.566 excluídas pelos recortes editoriais.
- **10 testes passaram**, incluindo a conferência de todos os parágrafos com os arquivos reais.
- Pacote construído e instalado em ambiente Python 3.11 isolado, com saídas idênticas às da execução pelo código-fonte.

As contagens seguem a regra documentada de palavras, sem números, com apóstrofos e hífens internos. A limpeza ainda mantém notas internas e alguns títulos; não se trata de um parser completo de capítulos e contos.

## Usar a busca literal e revisar as consultas

```bash
uv run python -m sherlock_search --query "Cyanea" --book the_case-book_of_sherlock_holmes.txt
uv run python -m sherlock_search.query_review
```

A busca retorna até cinco parágrafos com referências e contagem de ocorrências, ou informa ausência de correspondência literal. Ela procura a expressão informada, sem interpretar perguntas naturais. A revisão gera arquivos locais separados em `data/processed/review/`, com consultas e trechos para o autor conferir, sem executar busca ou métricas.

**Revisão concluída:** o autor aprovou as dez consultas de desenvolvimento e as vinte finais no chat. Os JSON registram `review_status: approved`; a [lista completa](docs/queries.md) apresenta as consultas e referências. Os trechos dos livros permanecem fora do Git; as propostas versionadas contêm apenas consultas, referências e justificativas.

A suíte atual tem **102 testes**, incluindo preparação, busca, CLI, avaliação, integração real e integridade do código embutido no notebook. As vinte consultas finais foram avaliadas somente após o congelamento do M3, conforme a seção seguinte.

## TF-IDF e desenvolvimento — M3

```bash
uv sync --python 3.11 --frozen
uv run python -m sherlock_search --method tfidf --query "Cyanea"
uv run python -m sherlock_search.development --check-freeze
```

Os dois métodos compartilham os mesmos parágrafos e referências. TF-IDF ordena por similaridade de cosseno; a pontuação não é probabilidade de correção. O índice é criado uma vez por instância e pode ser reutilizado nas consultas.

Nas dez consultas de desenvolvimento: a busca literal recuperou um trecho conhecido em **3/8 positivas**, com **0/2 negativas** retornando resultados; TF-IDF ficou em **1/8 positivas** e **2/2 negativas**. O corte selecionado foi **0,0**, excluindo scores iguais a zero: nenhum corte da grade reduziu retornos nas negativas sem perder o único acerto conhecido do TF-IDF. Não há evidência de superioridade do TF-IDF neste conjunto.

O [relatório de desenvolvimento](reports/m3_development.json) e o [snapshot congelado](evaluation/m3_freeze.json) permitem conferir o experimento antes do M4. Os rótulos são pequenos e não exaustivos; esses resultados não são uma avaliação independente nem comprovam desempenho em documentos empresariais. As vinte consultas finais não foram executadas no M3; a execução posterior do M4 está documentada abaixo.

## Notebook Kaggle e avaliação final — M4

[Notebook pronto para importar](notebooks/sherlock_document_search.ipynb) · [Resultados finais](reports/m4_final.json) · [Gráfico comparativo](reports/figures/retrieval_comparison.png) · [Instruções Kaggle](docs/kaggle-notebook.md)

| Método | Positivas com trecho conhecido no top 5 | Negativas com retorno indevido |
|---|---:|---:|
| Literal | 7/16 | 0/4 |
| TF-IDF | 8/16 | 4/4 |

O TF-IDF recuperou uma referência conhecida a mais, mas retornou resultados nas quatro negativas. Isso não demonstra superioridade geral. O corte e os quinze ativos M3 permaneceram congelados; nenhuma configuração ou rótulo foi ajustado com base nesses resultados.

O notebook foi reformulado para carregar um ZIP determinístico com código e metadados derivados de fontes verificadas; não clona nem baixa o código do projeto. O processamento usa Python 3.11.17 e as dependências congeladas em `uv.lock`, em ambiente separado do kernel. A versão reformulada executou oito células de código em kernel local limpo, sem erros, gerou dois gráficos e reproduziu o relatório final byte a byte. A execução atual no Kaggle ainda não foi conferida.

**Etapa do autor:** importar o arquivo no Kaggle, anexar o dataset, habilitar Internet e executar todas as células. A execução atual na plataforma e eventual publicação ainda não foram conferidas.

## V2 — BM25 e novo teste concluído

A v1 está preservada na tag `v1-baseline`. A v2 acrescenta BM25 em módulos separados, sem modificar o notebook ou os resultados históricos. O autor aprovou 36 novas consultas de desenvolvimento e 24 reservadas para teste. Consulte o [plano v2](docs/v2-plan.md), o [desenvolvimento](docs/v2-development.md) e a [avaliação final com gráfico e reprodução](docs/v2-final-evaluation.md).

```bash
uv run python -m sherlock_search.bm25 --query "Trichinopoly cigar"
uv run python -m sherlock_search.v2_development --output reports/v2/development.reproduced.json
```

No desenvolvimento, as consultas positivas com referência conhecida no top 5 foram: literal 9/27, TF-IDF 10/27 e BM25 12/27. TF-IDF e BM25 retornaram trechos nas nove negativas. No novo teste congelado, literal ficou em 6/18, TF-IDF em 10/18 e BM25 em 12/18, com 0/6, 6/6 e 6/6 negativas com retorno, respectivamente. BM25 foi avaliado como ranking; a ausência de resposta permanece sem solução. Estes números não devem ser comparados diretamente aos percentuais do teste v1, que usa outras consultas.

## Entregas do plano

1. Revisão humana de 30 consultas: dez para desenvolvimento e vinte reservadas para avaliação final, incluindo consultas sem resposta.
2. Comparação de busca literal por palavras ou expressões com busca por relevância usando TF-IDF.
3. Até cinco resultados com referências verificáveis, filtro por obra e mensagem quando não houver correspondência.
4. Notebook Jupyter para publicação e atualização no Kaggle pelo autor.
5. Relatório Quarto no GitHub Pages e dashboard Streamlit no Community Cloud, reaproveitando a lógica Python.

As consultas serão em inglês; a interface e o relatório, em português, com um resumo do projeto em inglês. A análise de apoio cobre tamanho dos textos, termos frequentes e qualidade da preparação. Chatbot e geração de respostas ficam fora da primeira versão.

O plano foi confirmado em 25 de outubro de 2026. O M1 foi aprovado e o M2 autorizado; M3 foi autorizado e concluído; M4 tem resultados finais e notebook reformulado validados localmente; a execução atual no Kaggle ainda não foi conferida. M5–M6 não começaram. A disponibilidade de quatro horas semanais durante seis semanas continua uma referência, com reestimativa após a revisão humana das consultas.

## Dados e documentação

Fonte: [Sherlock Holmes Series, no Kaggle](https://www.kaggle.com/datasets/talesgomes27/sherleck-books), com nove TXT na versão exibida durante a descoberta. O snapshot é identificado por SHA-256 por arquivo; os detalhes de origem e as condições de uso para publicação de trechos permanecem documentados separadamente.

- [Notebook, avaliação final e validação do M4](docs/kaggle-notebook.md)
- [TF-IDF, calibração e limites do M3](docs/tfidf-search.md)
- [Busca literal e seus limites](docs/literal-search.md)
- [Revisão das 30 consultas e protocolo](docs/query-review.md)
- [Lista completa das consultas aprovadas](docs/queries.md)
- [Preparação, comandos e limitações do M1](docs/data-preparation.md)
- [Relatório numérico do M1](reports/m1_quality.json)
- [Manifesto de arquivos e hashes](src/sherlock_search/corpus_manifest.json)
- [Proveniência e pendências de uso](docs/provenance.md)
- [Plano e marcos aprovados](docs/plan.md)
- [Descoberta e decisões](docs/discovery.md)
- [Glossário](GLOSSARY.md)
- [Registro de execução e verificações](task.md)

## English summary

Sherlock Document Search is a Python portfolio project for document retrieval and text analytics. The first milestone validates nine source files and prepares traceable paragraphs. Literal and TF-IDF retrieval are implemented, with 30 query labels approved by the project author. Only ten development queries were used for calibration. The twenty final queries have been evaluated without retuning. The Kaggle notebook embeds a deterministic code-and-metadata bundle and uses the attached corpus; the current hosted execution has not been checked. The Quarto report and Streamlit application are planned later. Evaluation on this literary corpus does not establish performance on business documents.
