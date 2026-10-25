# Sherlock Document Search

Projeto em planejamento: busca documental e análise exploratória do acervo Sherlock Holmes, com Python.

O objetivo é demonstrar competências aplicáveis a serviços freelancer: preparação de textos, recuperação de informação, avaliação de resultados e comunicação analítica. Resultados no corpus literário não comprovam desempenho em documentos de clientes nem retorno comercial.

## Entregas pretendidas

- Processamento e busca em Python.
- Notebook Jupyter para publicação e atualização no Kaggle pelo autor.
- Relatório Quarto para GitHub Pages.
- Dashboard posterior em Streamlit.

## Estado atual

As quatro rodadas de decisões foram aprovadas em 25 de outubro de 2026. O plano consolidado aguarda confirmação final antes da implementação; ainda não há notebook executável, relatório publicado ou dashboard.

Planejamento de referência: quatro horas semanais durante seis semanas, sujeito à inspeção dos arquivos e ao escopo final. O aprendizado se concentra em NLP e avaliação de busca, aproveitando a experiência prévia em Python e análise de dados.

A demonstração é voltada a pequenas equipes que precisam localizar informações em acervos documentais. As consultas serão em inglês na primeira versão, com interface e relatório em português e um resumo do projeto em inglês.

A avaliação incluirá revisão humana de 30 consultas: dez para desenvolvimento e vinte reservadas para a avaliação final, incluindo consultas sem resposta. Os critérios e os marcos estão descritos no plano.

## Escopo aprovado da primeira versão

- Comparar busca literal por palavras ou expressões com busca por relevância usando TF-IDF.
- Apresentar até cinco trechos, com título da obra, arquivo, localização verificável e filtro por obra; informar quando não houver correspondência.
- Apoiar a análise com tamanho dos textos, termos frequentes e qualidade da preparação dos dados.

A unidade inicial de busca será o parágrafo, preservando arquivo e intervalo de linhas de origem. Geração de respostas e chatbot ficam fora desta versão. O dashboard será hospedado no Streamlit Community Cloud e o relatório no GitHub Pages; essas publicações ainda não foram executadas.

## Documentação

- [Plano e marcos para confirmação final](docs/plan.md)
- [Descoberta e decisões aprovadas](docs/discovery.md)
- [Glossário do domínio](GLOSSARY.md)

## Dados

Fonte: [Sherlock Holmes Series, no Kaggle](https://www.kaggle.com/datasets/talesgomes27/sherleck-books).

Na consulta de 25 de outubro de 2026, o explorador exibia a versão 3, com nove arquivos TXT e tamanho total informado de 4,04 MB. A descrição enumera seis obras. A amostra de `a_study_in_scarlet.txt` está em inglês e inclui cabeçalho do Project Gutenberg. A inspeção do ZIP confirmou os nove nomes, a codificação UTF-8 com BOM e separadores de parágrafos; os detalhes e o hash do download estão no registro de descoberta.

Por decisão aprovada, os textos originais ficam fora do Git; a documentação registrará como obtê-los e identificar a versão utilizada. No notebook Kaggle, o corpus será anexado como entrada. A licença exibida no Kaggle é “Other (specified in description)”; a origem e as condições de uso de cada arquivo ainda precisam ser verificadas antes de definir redistribuição.
