# V2 — por que as consultas sem resposta ainda recebem resultados

## Escopo e evidência

Esta análise usa a implementação congelada de TF-IDF e BM25, os parâmetros registrados em `evaluation/v2/configuration_decision.json` e os IDs e scores já publicados em `reports/v2/final.json`. As seis perguntas e seus rótulos foram conferidos em `evaluation/v2/final.json`; nenhuma consulta foi criada ou alterada. Para explicar a sobreposição lexical, os tokens foram inspecionados descritivamente com o `build_analyzer` do `CountVectorizer` configurado com `stop_words="english"`, junto aos parágrafos localmente referenciados pelos IDs do top 1. Não houve ajuste, nova busca, ajuste de parâmetros ou cópia de trechos dos livros para este relatório.

A configuração decidiu avaliar BM25 como ranker, com `k1=1.2`, `b=0.75`, `min_score=0.0`, sem regra adicional de abstenção. A decisão registra que o corte candidato 32, estudado no desenvolvimento, eliminou os 12 acertos positivos e foi rejeitado. Portanto, o retorno de negativos não é uma falha de um limiar omitido por acidente: a v2 não declara que resolveu answerability.

## O que os top 1 mostram

Scores e IDs abaixo são cópias dos resultados pré-computados. As sobreposições resumem a inspeção dos tokens do top 1 e explicam a relação lexical observada; não são respostas aos detalhes pedidos.

| ID | Detalhe pedido (resumo) | Por que o top 1 parece relacionado | TF-IDF: top 1 | BM25: top 1 |
| --- | --- | --- | --- | --- |
| `v2-final-19` | Idades dos dois cavalos de Jefferson Hope no Eagle Ravine | O top 1 repete os cavalos e o local de espera; informa quantidade e local, não idade. | `a_study_in_scarlet.txt:3619-3621` — **0.500125087742** | `a_study_in_scarlet.txt:3619-3621` — **29.116356649083** |
| `v2-final-20` | Preço cobrado pela funerária pelo caixão ampliado | O top 1 BM25 compartilha “Poultney Square”; o top 1 TF-IDF só compartilha “delivered”. A localização e a entrega não informam o preço do caixão. | `the_hound_of_the_baskervilles.txt:2821-2821` — **0.320414488583** | `his_last_bow.txt:5127-5129` — **12.880155475205** |
| `v2-final-21` | Tarifa ferroviária de Reading a Eyford | O top 1 BM25 menciona Victor Hatherley e uma jornada; isso não informa a tarifa. O top 1 TF-IDF compartilha apenas “journey”. | `the_return_of_sherlock_holmes.txt:10682-10682` — **0.315162381308** | `the_adventures_of_sherlock_holmes.txt:7987-7992` — **14.715547556931** |
| `v2-final-22` | Nome do navio que levaria Selden à América do Sul | O top 1 BM25 trata de empresas sul-americanas e compartilha “South America”; não é o navio nem dá seu nome. O top 1 TF-IDF compartilha “expected”. | `the_adventures_of_sherlock_holmes.txt:1768-1768` — **0.373250605946** | `the_return_of_sherlock_holmes.txt:5937-5940` — **13.511484638777** |
| `v2-final-23` | Peso exato, em libras, do cofre vazio de Agra | O título do capítulo no top 1 BM25 contém “Agra” e “treasure”; o top 1 TF-IDF compartilha “Mary”. Tema e nomes não fornecem peso físico. | `the_adventures_of_sherlock_holmes.txt:10627-10627` — **0.342986219068** | `the_sign_of_the_four.txt:3409-3410` — **16.926443442346** |
| `v2-final-24` | Calibre da munição que matou o engenheiro Menzies | O top 1 BM25 menciona o engenheiro e a mina Crow Hill; o top 1 TF-IDF compartilha “kill”. A cena relacionada não informa calibre. | `the_valley_of _fear.txt:6063-6063` — **0.324113508911** | `the_valley_of _fear.txt:5804-5809` — **17.273226884234** |

Isso também explica por que um score apreciável pode acompanhar uma passagem insuficiente: o ranking mede sinais de correspondência no texto, não se o texto prova o atributo solicitado. No caso do caixão, por exemplo, o top 1 TF-IDF é selecionado com a sobreposição lexical mínima “delivered”; para outros casos, o termo compartilhado é tópico, como “journey”, “South America” ou “Agra treasure”. A ausência de score zero não contradiz os rótulos aprovados: estes perguntam por um atributo específico que as justificativas dizem não estar informado no contexto revisado.

## Mecânica dos scores

- **TF-IDF:** `TfidfSearch` usa `TfidfVectorizer(stop_words="english")`, transforma a consulta no vocabulário aprendido no corpus e ordena pela similaridade de cosseno. Termos funcionais removidos não contribuem. Termos fora do vocabulário também não contribuem, mas não anulam outros termos úteis: se restar ao menos um termo da consulta com peso e houver interseção com um parágrafo, o cosseno pode ser positivo. A busca só descarta score zero, exige `score >= min_score` e o `min_score` congelado é zero. Logo, qualquer interseção positiva restante pode entrar no top 5. Similaridade de cosseno é uma medida geométrica entre vetores; o valor TF-IDF não é probabilidade de a pergunta ser respondível.
- **BM25:** a implementação considera cada termo distinto da consulta uma vez e soma os pesos dos termos presentes no parágrafo. O IDF aplicado é `log1p((N-df+0.5)/(df+0.5))`, positivo para termos do vocabulário; com qualquer termo compartilhado, a soma pode ser positiva. O corte também é zero, e só scores positivos são retornados. Scores BM25 são pesos de relevância sem limite probabilístico; seus valores não são comparáveis à escala de similaridade TF-IDF.
- **Ambos:** são rankers lexicais, não classificadores de answerability. `min_score=0.0` permite qualquer correspondência positiva; não existe no fluxo uma verificação de que o top 1 contenha a resposta ou todos os atributos pedidos. TF-IDF e BM25 podem identificar um trecho tematicamente útil e ainda retorná-lo indevidamente sob um protocolo de QA que exige abstenção quando o detalhe não está sustentado.

A diferença entre ranking e answerability importa para estes casos: trechos sobre a fuga, a jornada, a América do Sul, o tesouro ou o ataque podem orientar uma leitura, sem estabelecer idade, preço, tarifa, nome ou calibre. A avaliação classifica “retorno em consulta negativa” como falso positivo do protocolo QA; isso não afirma que cada trecho retornado seja irrelevante ao tópico.

## Limites do resultado

Na avaliação final, TF-IDF e BM25 tiveram algum retorno em **6/6 consultas negativas** aprovadas; isso significa seis consultas com ao menos um resultado, não que todo o acervo tenha sido retornado. A busca literal teve **0/6** retornos nessas mesmas perguntas porque não encontrou a sequência exata; esse zero não é evidência semântica de ausência. As negativas aprovadas são seis exemplos limitados, construídos como detalhes plausíveis não informados em escopos narrativos revisados. A revisão contextual não prova ausência formal em todo o acervo, e as referências de resposta são conhecidas, não exaustivas.

O conjunto v2 já foi aberto, executado e divulgado. Seus resultados de desenvolvimento aprovado e final foram ambos observados; eles não são testes independentes para selecionar ajustes e alegar validação independente de uma v3. Qualquer avaliação da próxima versão precisa de um novo conjunto reservado, criado e congelado antes dos ajustes.

## Melhorias futuras a avaliar

1. Ampliar e diversificar o conjunto de desenvolvimento com negativas difíceis (*hard negatives*), cobrindo correspondência de entidade, tópico e evento quando falta justamente um atributo solicitado.
2. Tratar abstenção como decisão separada do ranking: desenvolver sinais candidatos, como score do top 1, margem entre candidatos e cobertura de termos/atributos da pergunta. Cada sinal exige validação; nenhum deles, isoladamente, garante que a resposta está ausente ou presente.
3. Avaliar embeddings como forma potencial de ampliar recall lexicalmente distante. Eles não resolvem por si só a abstenção nem provam answerability. Um cross-encoder/reranker pode ajudar a julgar a relevância fina dos candidatos recuperados, mas também não garante que o corpus sustente uma resposta.
4. Antes de qualquer novo ajuste, reservar um novo teste independente e mantê-lo fechado até congelar a próxima configuração. Não reutilizar v2 para calibrar e depois reportar esses mesmos resultados como estimativa independente.

Como primeira experiência de uma próxima versão, eu rotularia pares pergunta–trecho em três categorias: sustenta a resposta, relacionado sem o detalhe pedido e irrelevante. Isso permite testar uma decisão de evidência separada da ordenação. Seu corte ou modelo seria escolhido somente no desenvolvimento, medindo também quantas consultas positivas ficam sem resultado. Um novo teste reservado deve anteceder esses ajustes. Esta é uma proposta, não uma melhoria já validada.

## Fontes técnicas

- [Scikit-learn: extração de features de texto e stop words](https://scikit-learn.org/stable/modules/feature_extraction.html) explica a representação TF-IDF, a lista inglesa e seus limites.
- [Scikit-learn: similaridade de cosseno](https://scikit-learn.org/stable/modules/metrics.html#cosine-similarity) define-a como produto interno de vetores normalizados, não probabilidade.
- [Apache Lucene: BM25Similarity](https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/search/similarities/BM25Similarity.html) documenta a fórmula IDF BM25 e os parâmetros `k1` e `b`. A implementação deste projeto é própria e sua fórmula foi lida diretamente em `src/sherlock_search/bm25.py`.
- [Augmented SBERT (NAACL 2021)](https://aclanthology.org/2021.naacl-main.28/) descreve a diferença prática entre bi-encoders e cross-encoders e o compromisso entre eficiência e comparação conjunta; não estabelece garantia de answerability.
