# Proveniência do corpus

Fonte de distribuição: [Sherlock Holmes Series, no Kaggle](https://www.kaggle.com/datasets/talesgomes27/sherleck-books). A versão exibida durante a descoberta foi 3. Os hashes no [manifesto](../src/sherlock_search/corpus_manifest.json) identificam o snapshot efetivamente preparado, sem depender de o endpoint manter a mesma resposta no futuro.

Inspeção realizada em 25 de outubro de 2026. Os nove cabeçalhos dos TXT identificam Arthur Conan Doyle e declaram inglês. Os IDs e datas abaixo foram lidos nos arquivos; os links das edições são derivados desses IDs e não afirmam que as páginas atuais reproduzem os mesmos bytes do snapshot Kaggle.

| Arquivo | Edição declarada | Release declarado | Atualização declarada | Crédito de produção no cabeçalho |
|---|---|---|---|---|
| `a_study_in_scarlet.txt` | [Gutenberg #244](https://www.gutenberg.org/ebooks/244) | abril de 1995 | 30/09/2016 | Roger Squires |
| `his_last_bow.txt` | [Gutenberg #2350](https://www.gutenberg.org/ebooks/2350) | outubro de 2000 | 18/09/2022 | David Brannan |
| `the_adventures_of_sherlock_holmes.txt` | [Gutenberg #1661](https://www.gutenberg.org/ebooks/1661) | 29/11/2002 | 20/05/2019 | Voluntário anônimo do Project Gutenberg e Jose Menendez |
| `the_case-book_of_sherlock_holmes.txt` | [Gutenberg #69700](https://www.gutenberg.org/ebooks/69700) | 04/01/2023 | Não declarada | Al Haines |
| `the_hound_of_the_baskervilles.txt` | [Gutenberg #2852](https://www.gutenberg.org/ebooks/2852) | outubro de 2001 | 27/06/2021 | Shreevatsa R e David Widger |
| `the_memoirs_of_sherlock_holmes.txt` | [Gutenberg #834](https://www.gutenberg.org/ebooks/834) | março de 1997 | 27/04/2022 | Angela M. Cable |
| `the_return_of_sherlock_holmes.txt` | [Gutenberg #108](https://www.gutenberg.org/ebooks/108) | fevereiro de 1994 | 27/04/2022 | Voluntário anônimo |
| `the_sign_of_the_four.txt` | [Gutenberg #2097](https://www.gutenberg.org/ebooks/2097) | março de 2000 | 25/04/2022 | Não identificado no cabeçalho |
| `the_valley_of _fear.txt` | [Gutenberg #3776](https://www.gutenberg.org/ebooks/3776) | fevereiro de 2003 | 10/02/2005 | Toby F. Charkin; versão HTML por Al Haines |

Uma inspeção externa consultou os registros atuais de #244 e #69700 e a [página oficial de licença do Project Gutenberg](https://www.gutenberg.org/policy/license.html). Os sete outros registros não foram verificados individualmente na web nesta etapa. Em #69700, os metadados atuais indicam atualização posterior ao cabeçalho do TXT Kaggle; por isso, a página atual não substitui a identificação por hash do arquivo utilizado.

Os nove TXT contêm aviso ou licença Project Gutenberg. Os avisos de reutilização variam entre edições e remetem aos termos incluídos ou à página de licença. A página oficial distingue condições relativas ao texto e ao uso da marca Project Gutenberg e orienta a verificação das regras locais. Esses registros são documentação de origem e não constituem um parecer sobre direitos de publicação.

O rótulo de licença observado no Kaggle foi “Other (specified in description)”. A verificação das condições aplicáveis à exibição pública de trechos permanece pendente, incluindo os registros individuais, os termos dos arquivos e a descrição atual do dataset. A presença do cabeçalho Gutenberg e a manutenção dos TXT fora do Git não resolvem essa verificação por si sós.

Neste marco, apenas código, metadados e contagens são candidatos a versionamento. Os originais preservam os avisos e créditos completos em `data/raw/`; parágrafos e outros derivados que reproduzam texto ficam em `data/processed/`, também ignorado pelo Git. A exibição pública de trechos pertence aos marcos de relatório e dashboard, após resolver as pendências de uso e atribuição.
