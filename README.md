# Sherlock Document Search

Projeto Python de busca documental e análise exploratória do acervo Sherlock Holmes. O **M1 — dados e preparação** está implementado e validado; a busca, o notebook Kaggle, o relatório Quarto e o dashboard Streamlit pertencem aos próximos marcos.

O objetivo é demonstrar competências aplicáveis a serviços freelancer: preparação de textos, recuperação de informação, avaliação de resultados e comunicação analítica. O exemplo é voltado a pequenas equipes que precisam localizar informações em acervos documentais. Resultados no corpus literário não comprovam desempenho em documentos de clientes nem retorno comercial.

## Executar o M1

Com Python 3.11 ou superior e uv, na raiz do repositório:

```bash
uv sync --python 3.11
uv run python -m sherlock_search --download
uv run python -m unittest discover -s tests -v
```

O pacote usa apenas a biblioteca padrão em execução. O download cria `data/raw/` e recusa sobrescrever uma pasta existente; para reutilizar os TXT e gerar novamente as saídas, execute `uv run python -m sherlock_search` sem `--download`.

Saídas locais: `data/processed/paragraphs.jsonl`, com texto e linhas de origem, e `data/processed/quality.json`, com metadados e contagens. Os originais e os parágrafos preparados ficam fora do Git. A instalação inicial e o download exigem rede; a preparação de dados já disponíveis pode executar sem rede.

## Resultado do M1

- **9 arquivos verificados**, 4.041.127 bytes.
- **15.598 parágrafos**, cada um com título da obra, nome do arquivo e intervalo de linhas de origem.
- **656.884 palavras retidas**; 29.566 excluídas pelos recortes editoriais.
- **10 testes passaram**, incluindo a conferência de todos os parágrafos com os arquivos reais.
- Pacote construído e instalado em ambiente Python 3.11 isolado, com saídas idênticas às da execução pelo código-fonte.

As contagens seguem a regra documentada de palavras, sem números, com apóstrofos e hífens internos. A limpeza ainda mantém notas internas e alguns títulos; não se trata de um parser completo de capítulos e contos.

## Próximas entregas aprovadas

1. Revisão humana de 30 consultas: dez para desenvolvimento e vinte reservadas para avaliação final, incluindo consultas sem resposta.
2. Comparação de busca literal por palavras ou expressões com busca por relevância usando TF-IDF.
3. Até cinco resultados com referências verificáveis, filtro por obra e mensagem quando não houver correspondência.
4. Notebook Jupyter para publicação e atualização no Kaggle pelo autor.
5. Relatório Quarto no GitHub Pages e dashboard Streamlit no Community Cloud, reaproveitando a lógica Python.

As consultas serão em inglês; a interface e o relatório, em português, com um resumo do projeto em inglês. A análise de apoio cobre tamanho dos textos, termos frequentes e qualidade da preparação. Chatbot e geração de respostas ficam fora da primeira versão.

O plano foi confirmado em 25 de outubro de 2026, com autorização para M1. O M1 aguarda aceite; M2–M6 não começaram. A disponibilidade de quatro horas semanais durante seis semanas continua uma referência, com reestimativa após a revisão humana das consultas.

## Dados e documentação

Fonte: [Sherlock Holmes Series, no Kaggle](https://www.kaggle.com/datasets/talesgomes27/sherleck-books), com nove TXT na versão exibida durante a descoberta. O snapshot é identificado por SHA-256 por arquivo; os detalhes de origem e as condições de uso para publicação de trechos permanecem documentados separadamente.

- [Preparação, comandos e limitações do M1](docs/data-preparation.md)
- [Relatório numérico do M1](reports/m1_quality.json)
- [Manifesto de arquivos e hashes](src/sherlock_search/corpus_manifest.json)
- [Proveniência e pendências de uso](docs/provenance.md)
- [Plano e marcos aprovados](docs/plan.md)
- [Descoberta e decisões](docs/discovery.md)
- [Glossário](GLOSSARY.md)
- [Registro de execução e verificações](task.md)

## English summary

Sherlock Document Search is a Python portfolio project for document retrieval and text analytics. The first milestone validates nine source files and prepares traceable paragraphs; lexical search, TF-IDF evaluation, a Kaggle notebook, a Quarto report and a Streamlit application are planned next. Evaluation on this literary corpus does not establish performance on business documents.
