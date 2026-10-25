# M1 — obtenção, preparação e rastreabilidade

O M1 implementa a preparação do snapshot de nove TXT identificado no [manifesto](../src/sherlock_search/corpus_manifest.json). A validação exige os nomes originais, tamanhos e SHA-256 dos arquivos antes de extrair qualquer parágrafo. Isso inclui o espaço em `the_valley_of _fear.txt`.

## Reprodução

Na raiz do repositório, com Python 3.11 ou superior e uv:

```bash
uv sync --python 3.11
uv run python -m sherlock_search --download
uv run python -m unittest discover -s tests -v
```

O primeiro comando instala o pacote local. O segundo acessa o endpoint público do Kaggle, verifica tamanho e hash do ZIP, inventário e hashes dos nove TXT e cria `data/raw/`. Não exige credenciais. A opção `--download` recusa uma pasta de origem que já exista, protegendo os arquivos anteriores; para repetir a preparação, use:

```bash
uv run python -m sherlock_search
```

Também é possível fornecer os TXT previamente obtidos, como no futuro notebook Kaggle:

```bash
uv run python -m sherlock_search --raw-dir CAMINHO_DOS_NOVE_TXT --output-dir data/processed
```

O caminho deve apontar diretamente à pasta que contém os nove arquivos. Um inventário, tamanho ou hash diferente interrompe o processamento, com mensagem para conferir a origem. Não se deve atualizar o manifesto apenas para contornar essa verificação: outro snapshot exige revisão dos limites e dos resultados.

O download e a instalação inicial dependem de rede. A preparação de uma pasta já verificada usa apenas a biblioteca padrão e pode executar sem rede. O ZIP original pode ser obtido pelo [endpoint oficial](https://www.kaggle.com/api/v1/datasets/download/talesgomes27/sherleck-books); a rotina não mantém uma segunda cópia do ZIP em disco, mas registra seu tamanho e hash esperados no manifesto.

## Saídas locais e dados versionados

- `data/raw/`: os TXT originais, sem regravar conteúdo, normalizar terminadores ou retirar BOM.
- `data/processed/paragraphs.jsonl`: um objeto por parágrafo, com `id`, `filename`, `title`, `line_start`, `line_end` e `text`.
- `data/processed/quality.json`: contagens por arquivo e totais, sem trechos dos livros.
- [reports/m1_quality.json](../reports/m1_quality.json): cópia versionada do relatório numérico da execução validada do M1.

Os diretórios de dados e os ZIP ficam fora do Git. O manifesto contém apenas metadados, identificadores, hashes e limites de linhas. As saídas preparadas podem ser sobrescritas ao repetir a execução; os TXT de origem são somente lidos. A reprodução deve gerar o mesmo relatório numérico e os mesmos parágrafos para este snapshot e esta implementação.

## Linhas, parágrafos e limpeza

A referência usa linhas numeradas a partir de 1, com início e fim inclusivos no TXT original. A leitura trata BOM UTF-8 e terminadores CRLF, LF ou CR em memória. Separadores Unicode dentro de uma linha não criam novas linhas de origem. Os nove arquivos inspecionados usam CRLF.

Dentro do intervalo narrativo revisado por arquivo, uma linha vazia ou composta só por espaços separa parágrafos. Retiram-se os espaços das pontas de cada linha e juntam-se as linhas de um parágrafo com um espaço. Nenhuma linha é removida ou renumerada antes de capturar sua referência. O identificador é `filename:line_start-line_end`; sua estabilidade é relativa ao snapshot verificado.

Os limites revisados excluem créditos iniciais, prefácios, sumários e os rodapés de distribuição. Em *A Study in Scarlet*, o recorte termina antes das notas do transcritor; em *The Case-Book*, termina antes de anúncios editoriais. Os marcadores finais `THE END` de *The Hound* e *The Return* também ficam fora. Os primeiros cabeçalhos narrativos não são necessários para localizar os trechos; o título da obra vem do manifesto.

Essa limpeza não identifica automaticamente todos os títulos de contos ou capítulos nem remove todas as notas internas, marcas de itálico ou chamadas de notas. Algumas quebras editoriais dentro da narrativa permanecem como parágrafos. A unidade aqui é um parágrafo do arquivo, não uma garantia de unidade semântica completa. A adoção de outro snapshot exige nova revisão desses limites.

## Contagem de palavras

A contagem usa grupos de letras Unicode, permitindo apóstrofo reto ou curvo e hífen internos. Números, inclusive frações e números Unicode como `½`, são excluídos; palavras compostas como `two-line` e formas como `Watson's` contam uma unidade cada. Não há remoção de stopwords nessa contagem.

O relatório compara o TXT completo com os parágrafos retidos. A diferença indica palavras excluídas pelos recortes; não estima a quantidade total de ruído editorial nem a qualidade da busca, ainda não implementada.

## Resultado verificado em 25 de outubro de 2026

| Medida | Resultado |
|---|---:|
| Arquivos verificados | 9 |
| Bytes dos TXT | 4.041.127 |
| Linhas de origem | 80.571 |
| Palavras nos TXT completos | 686.450 |
| Palavras retidas | 656.884 |
| Palavras excluídas pelos recortes | 29.566 |
| Parágrafos retidos | 15.598 |

Os testes usam exemplos sintéticos identificados e, quando o corpus está disponível, os nove arquivos reais. O teste real compara todos os parágrafos às linhas de origem, verifica a unicidade dos IDs e confere limites finais que poderiam truncar a narrativa ou reter marcadores editoriais.

Sem `data/raw/`, o teste real é marcado como ignorado; isso não equivale a validar o corpus. Para usar uma pasta externa nos testes, defina `SHERLOCK_RAW_DIR` no ambiente. A execução do M1 incluiu o corpus real, sem teste ignorado.

O pacote foi construído como sdist e wheel, instalado em ambiente Python 3.11 isolado e executado fora da árvore do código-fonte. Os resultados foram comparados byte a byte com a execução pelo código-fonte. Isso valida o empacotamento deste marco, não a execução no Kaggle, reservada ao M4.

## Proveniência e continuidade

O [registro de proveniência](provenance.md) identifica as edições digitais declaradas nos cabeçalhos e as verificações ainda necessárias antes da publicação de trechos. A preparação não modifica nem elimina a licença dos arquivos originais; a licença deixa apenas de ser indexada no texto narrativo preparado.

O M1 não exige revisão humana de consultas. Essa participação será necessária no M2. A estimativa de 24 horas continua sendo referência: a inspeção não exigiu parser geral, mas a duração da revisão das 30 consultas ainda não foi medida. O próximo ponto de reestimativa será após essa revisão.
