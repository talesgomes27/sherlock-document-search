# V2 — desenvolvimento com BM25

O autor aprovou as 36 consultas de desenvolvimento e as 24 reservadas no chat em 25 de outubro de 2026. O aceite global foi registrado, sem afirmar auditoria individual de cada caso. As perguntas e os rótulos factuais não foram alterados após as primeiras métricas; apenas os status passaram a `approved`.

## Executar

```bash
uv sync --python 3.11.17 --frozen
uv run python -m sherlock_search.bm25 --query "Trichinopoly cigar"
uv run python -m sherlock_search.v2_development --output reports/v2/development.reproduced.json
```

A CLI BM25 informa título, ID, linhas e score, sem gerar respostas. O filtro `--book` aceita o nome exato do TXT; `--min-score` é um corte BM25 não negativo, sem interpretação probabilística. A CLI v1 continua intacta. O comparador lê somente `evaluation/v2/development.json`, sem opção para escolher outro conjunto; o teste reservado não é usado na calibração. Saídas do comparador ficam em `reports/v2/`.

## Resultado de desenvolvimento

Todos os métodos abaixo usam as mesmas 27 consultas positivas, nove negativas, parágrafos e top 5. Estas são métricas de desenvolvimento, não uma estimativa independente de generalização.

| Método | Consultas positivas com referência conhecida no top 5 | Negativas com retorno | MRR@5 nas positivas |
|---|---:|---:|---:|
| Literal v1 | 9/27 | 0/9 | 0.2901 |
| TF-IDF v1 | 10/27 | 9/9 | 0.2111 |
| BM25 sem corte adicional | 12/27 | 9/9 | 0.2994 |
| BM25 com corte candidato 32 | 0/27 | 3/9 | 0.0000 |

BM25 encontrou referência conhecida em mais consultas positivas deste conjunto, mas retornou trechos em todas as negativas. Isso não demonstra superioridade geral. Os julgamentos são não exaustivos: um ID ausente pode coexistir com outros trechos relevantes. Nas questões de contexto, um hit conhecido também não garante evidência completa para todas as partes da pergunta.

## Leitura por tipo de consulta

Cada grupo positivo tem nove perguntas. Os hits conhecidos foram:

| Tipo | Literal | TF-IDF | BM25 sem corte |
|---|---:|---:|---:|
| Palavra ou expressão exata | 9/9 | 8/9 | 8/9 |
| Paráfrase | 0/9 | 0/9 | 0/9 |
| Contexto | 0/9 | 2/9 | 4/9 |

O ganho agregado BM25 veio de perguntas de contexto deste desenvolvimento; as paráfrases continuam uma limitação importante dos métodos lexicais. Isso ajuda a formular uma hipótese futura sobre busca semântica, mas não autoriza acrescentar outro modelo após observar o novo teste e apresentar a repetição como validação independente.

## Corte estudado e decisão registrada

A regra registrada no commit `da31d56`, antes das métricas, maximiza a média entre recuperação conhecida e abstenção, com desempates por menor retorno nas negativas e menor corte. O resultado dessa regra foi 32: perdeu os doze acertos e deixou as 27 positivas sem resultado. Não se mudou a regra para esconder esse resultado.

O candidato não foi adotado por inviabilidade funcional. A decisão em `evaluation/v2/configuration_decision.json`, feita antes de abrir o novo teste, é avaliar BM25 como mecanismo de ranking com k1=1,2, b=0,75 e min_score=0,0, sem alegar resolução da ausência de resposta. Os cortes testados que preservaram acertos não reduziram os retornos nas negativas. Abstenção continua um problema aberto para outro ciclo de desenvolvimento.

## Preservação e próximos gates

A tag `v1-baseline` identifica o commit `8f17985`. Os quinze ativos M3, o relatório final M4 e os demais 35 ativos do manifesto v1 permanecem inalterados; o notebook v1 continua histórico. O pacote mantém as dependências congeladas. Não se adicionaram embeddings, banco vetorial ou serviços externos.

O novo teste tem 24 consultas aprovadas e permanece reservado ao avaliador até o congelamento v2. Sua curadoria foi feita por subagente separado, sem executar recuperação; o implementador não consultou suas perguntas ou referências. Antes de executar, o novo avaliador recebe testes sintéticos e revisão independente. Depois do congelamento, os três métodos serão avaliados nas mesmas consultas, sem novos ajustes.

As referências de desenvolvimento ficam em 20–45% dos corpos das obras e as reservadas em 60–85%; isso não elimina sozinho dependências narrativas. O curador também verificou intenções repetidas. Negativas são detalhes plausíveis não informados no escopo inspecionado; essa revisão não prova ausência formal em todo o acervo. A primeira proposta usava premissas refutadas e foi corrigida antes das métricas, pois trechos que refutam uma pergunta podem ser úteis.

Os relatórios JSON de desenvolvimento registram construção do índice e média local por consulta. Tempos são descritivos, variam entre execuções e não são benchmark de produção. Os relatórios do código-fonte e do wheel instalado coincidiram nos resultados; diferenças de tempo são esperadas.

## Avaliação posterior

O novo teste foi executado após congelamento, sem novos ajustes, e depois divulgado para reprodução. Veja [avaliação final v2](v2-final-evaluation.md). Os trechos que descrevem a reserva acima registram o procedimento anterior à execução, não o estado de acesso atual.
