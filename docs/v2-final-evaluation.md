# V2 — avaliação final de busca documental

A configuração foi congelada no commit `14a0913`, depois da aprovação do autor e antes de executar as 24 consultas finais. O BM25 usa k1=1,2, b=0,75 e min_score=0,0. Nenhum parâmetro, rótulo ou recorte foi ajustado após a execução. Literal e TF-IDF são os métodos da v1, preservados.

## Resultado no novo teste

| Método | Consultas positivas com referência conhecida no top 5 (18) | Negativas com retorno (6 negativas) | MRR@5 nas positivas |
|---|---:|---:|---:|
| Literal v1 | 6/18 (33.3%) | 0/6 (0%) | 0.2963 |
| TF-IDF v1 | 10/18 (55.6%) | 6/6 (100%) | 0.3981 |
| BM25 | 12/18 (66.7%) | 6/6 (100%) | 0.4907 |

![Comparação v2: referências conhecidas recuperadas e consultas negativas com retorno](../reports/v2/figures/final_comparison.png)

BM25 encontrou referência conhecida em duas consultas a mais que TF-IDF neste teste e apresentou MRR maior. Os dois, entretanto, retornaram trechos nas seis consultas sem resposta. A busca literal retornou menos referências conhecidas e nenhum resultado nas negativas. A melhoria observada é de recuperação e ordenação neste conjunto; não demonstra superioridade geral nem identificação confiável da ausência de resposta.

Os denominadores são diferentes daqueles do teste v1 (16 positivas e quatro negativas). Comparações entre versões são feitas aqui executando os métodos no mesmo novo conjunto; não comparando diretamente percentuais de conjuntos distintos. A v1 original continua com seus resultados intactos.

MRR@5 é a média do inverso da posição da primeira referência conhecida, considerando somente as positivas e atribuindo zero quando ela não aparece no top 5. Maior é melhor; essa medida também depende das referências anotadas.

## Decisões e limitações

O corte 32 sugerido pela regra inicial foi rejeitado no desenvolvimento, pois eliminou todos os acertos positivos. A decisão de manter BM25 sem corte adicional foi registrada antes do novo teste; seu histórico está em [desenvolvimento](v2-development.md). A avaliação final não executa grades nem escolhe configurações.

As 24 consultas foram criadas por curador separado, com referências em região diferente do desenvolvimento e revisão de sobreposição de intenções. O autor aprovou os dois grupos no chat; não se afirma auditoria humana individual documentada. Referências são conhecidas e não exaustivas. Um hit pode ser evidência parcial e não equivale a responder integralmente uma pergunta de contexto. Negativas tratam detalhes plausíveis não informados no escopo inspecionado, sem provar formalmente ausência em todo o acervo. O conjunto pequeno e curado não sustenta desempenho em documentos de clientes.

Após esta avaliação, os [metadados finais](../evaluation/v2/final.json) e a [lista de consultas](v2-final-queries.md) foram publicados para reprodução. Esse teste já foi utilizado e divulgado: não é mais independente para selecionar melhorias futuras. Os TXT e os trechos de revisão continuam fora do Git.

## Reproduzir sem alterar o snapshot

Com o corpus original validado em `data/raw`, restaure a cópia local dos rótulos publicados em um clone novo e grave resultados em outro arquivo:

```bash
uv sync --python 3.11.17 --frozen
mkdir -p data/processed/v2_holdout
cp -n evaluation/v2/final.json data/processed/v2_holdout/final.json
uv run python -m sherlock_search.v2_final --output reports/v2/final.reproduced.json
```

O `cp -n` preserva eventual arquivo existente; o avaliador interrompe se seus bytes divergirem do snapshot. O JSON privado aprovado está no manifesto por hash e é byte-idêntico à cópia pública. O documento de revisão com trechos dos livros não é necessário à execução. Os estados `final_queries_executed: false` e `approved_not_evaluated` dos manifests são históricos, referentes ao congelamento; a execução posterior está registrada no relatório final e em `reports/v2/validation.json`. Não reescreva esses manifests para atualizar a cronologia.

Para reproduzir desenvolvimento, use saída nova, como `--output reports/v2/development.reproduced.json`. Não sobrescreva `development.approved.json`: ele faz parte do congelamento e contém tempos locais. O script de figuras lê apenas o relatório pronto e usa Matplotlib das ferramentas de validação do notebook; não executa buscas.

## Evidências e uso no portfólio

- [Resultado completo por consulta](../reports/v2/final.json), somente IDs e scores, sem texto das obras.
- [Evidência de validação](../reports/v2/validation.json).
- [Congelamento v2](../evaluation/v2/freeze.json) e [preservação v1](../evaluation/v2/v1_preservation.json).

Os 102 testes passaram no código-fonte e no wheel instalado, sem ignorar os testes do corpus real. O avaliador e seus testes sintéticos passaram por revisão independente antes de executar o novo teste. A reprodução do wheel gerou relatório idêntico byte a byte ao original. PNG e SVG foram exportados, com inspeção visual do gráfico. O novo teste não foi usado para refazer escolhas.

Para o portfólio, a contribuição demonstrada é comparar métodos com rastreabilidade, avaliar uma hipótese, descartar uma configuração inviável e comunicar um ganho acompanhado de limites. O notebook Kaggle v1 foi preservado; a integração dos resultados v2 em um novo notebook ou dashboard ainda não foi realizada.
