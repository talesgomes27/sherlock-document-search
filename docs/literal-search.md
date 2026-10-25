# Busca literal — M2

A busca literal usa os parágrafos verificados pelo M1 e retorna até cinco resultados, com título da obra, arquivo, intervalo inclusivo de linhas de origem e contagem de ocorrências. A ordenação prioriza maior contagem; empates usam nome do arquivo e linhas, de forma determinística.

## Usar pelo terminal

```bash
uv run python -m sherlock_search --query "Cyanea"
uv run python -m sherlock_search --query "Cyanea" --book the_case-book_of_sherlock_holmes.txt
```

O exemplo usa um termo do conjunto de desenvolvimento. `--book` recebe o nome exato do TXT, disponível no [manifesto](../src/sherlock_search/corpus_manifest.json). Para os arquivos diretamente em `data/`, acrescente `--raw-dir data`.

Sem resultados, a CLI informa `Nenhuma correspondência literal encontrada.` Consultas vazias ou compostas somente por pontuação também não produzem resultados. Obra desconhecida gera mensagem de erro. `--book` exige `--query`.

A consulta só lê o corpus e mostra resultados no terminal; não sobrescreve o JSONL ou o relatório do M1. A chamada sem `--query` mantém o comportamento de preparação original.

## Usar no núcleo Python

```python
from pathlib import Path
from sherlock_search.corpus import prepare_corpus
from sherlock_search.search import literal_search

paragraphs, _ = prepare_corpus(Path("data/raw"))
results = literal_search(
    paragraphs, "Cyanea", filename="the_case-book_of_sherlock_holmes.txt"
)
```

O retorno é uma lista de cópias dos parágrafos selecionados, acrescentando `score`, um inteiro com o número de ocorrências. As entradas originais não são modificadas. Não há índice persistente, modelo ou dependência de execução adicional.

## Semântica e limites

- A busca ignora diferenças entre maiúsculas e minúsculas usando `casefold`.
- Uma expressão de várias palavras é procurada na ordem informada. Espaços repetidos ou quebras entre as palavras da consulta são equivalentes a espaços no parágrafo.
- O conteúdo da consulta é escapado: pontos, asteriscos e outros símbolos não se tornam operadores de expressão regular.
- As fronteiras impedem correspondência dentro de uma sequência maior de letras, números ou sublinhados. Apóstrofos e hífens são pontuação nessas fronteiras; a convenção de contagem de palavras do M1 é uma operação distinta.
- Contam-se ocorrências não sobrepostas. O filtro por obra é aplicado antes do limite de cinco.

Esse método procura a expressão literal; uma pergunta natural não é decomposta em palavras independentes nem interpretada como uma pergunta a responder. Por isso, uma consulta pode não ter correspondência literal mesmo quando há um trecho semanticamente relevante no corpus. A comparação com TF-IDF pertence ao M3/M4.

Os testes cobrem palavra completa, caixa, espaços, pontuação, ausência, ranking, empates, filtro, limite, preservação de referências e ausência de mutação. A integração real verifica um termo de desenvolvimento no snapshot do M1. Não foram executadas buscas ou métricas nas vinte consultas finais.
