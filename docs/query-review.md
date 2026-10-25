# M2 — revisão das consultas e protocolo de separação

O M1 foi aprovado pelo usuário. O M2 implementa a busca literal e prepara as 30 consultas para revisão humana. A implementação da busca está validada tecnicamente, mas o marco ainda depende da revisão do autor; nenhuma proposta deve ser tratada como rótulo aprovado automaticamente.

## Arquivos e distribuição proposta

| Conjunto | Arquivo versionado | Consultas | Com resposta proposta | Sem resposta proposta |
|---|---|---:|---:|---:|
| Desenvolvimento | [development.json](../evaluation/development.json) | 10 | 8 | 2 |
| Final | [final.json](../evaluation/final.json) | 20 | 16 | 4 |

Entre as positivas de desenvolvimento há um termo, três expressões e quatro perguntas naturais, distribuídas por oito arquivos. Entre as positivas finais há quatro termos, quatro expressões e oito perguntas naturais, cobrindo os nove arquivos. As negativas são perguntas anacrônicas, com termos que também podem aparecer nos textos. Essa escolha facilita uma primeira avaliação controlada; não representa a distribuição de consultas de usuários reais.

Os dois conjuntos foram propostos por subagentes separados, antes de executar comparações por consulta. A mistura de tipos foi definida sem consultar rankings ou métricas. As vinte consultas finais e os trechos correspondentes não foram enviados ao contexto do agente que implementou a busca. Isso é separação de trabalho e de uso, não uma alegação de sigilo dos arquivos públicos.

## Como conferir

Com os TXT disponíveis, execute na raiz do projeto:

```bash
uv run python -m sherlock_search.query_review
```

Para usar os TXT que já existiam diretamente em `data/`, acrescente `--raw-dir data`. O comando verifica o snapshot e os IDs, gera dois arquivos locais em `data/processed/review/` e atualiza [split_manifest.json](../evaluation/split_manifest.json), com contagens e hashes dos arquivos de consulta. Ele não executa busca, ranking ou métrica.

Abra os arquivos locais `development.md` e `final.md` nessa pasta. Eles mostram a consulta em inglês, a intenção proposta, o título, as linhas e os trechos originais indicados. Os trechos permanecem fora do Git. Os arquivos de revisão são gerados e podem ser sobrescritos; registre decisões no chat ou nos JSON de origem, não somente no Markdown gerado.

Para cada consulta:

1. Confira se a informação pedida está clara e se o trecho indicado realmente a atende. Um trecho que apenas compartilha palavras pode não ser relevante.
2. Corrija ou acrescente IDs de parágrafos relevantes conhecidos, usando `filename:linha_inicial-linha_final`. Não se exige provar que todas as passagens relevantes foram identificadas; essa limitação deve acompanhar os resultados.
3. Para as negativas, confira se a informação solicitada está ausente do corpus. Anacronismo é justificativa inicial, não uma aprovação humana já realizada.
4. Informe no chat os IDs aprovados e as correções necessárias. Também é possível editar `review_status` para `approved` ou `needs_changes` nos JSON. O valor inicial é `pending`.

O agente aplicará no registro as aprovações explicitamente informadas pelo autor. Alterações nas consultas ou referências exigem nova conferência das fontes afetadas. A autorização para implementar o M2 não substitui a revisão semântica dos rótulos.

## Proteção da avaliação final

- O M2 valida estrutura, referências e duplicatas exatas normalizadas entre os dois arquivos. Essas verificações não executam recuperação nem usam acertos e erros finais para mudar o método.
- A revisão humana pode acessar ambos os grupos para conferir os rótulos. Desenvolvimento e ajustes posteriores usam somente as dez consultas de desenvolvimento.
- Após o autor revisar as propostas, registrar os hashes dos arquivos aprovados. Fechar também código e parâmetros antes da avaliação final de M4; os hashes atuais identificam apenas as propostas, ainda não um benchmark aprovado e congelado.
- Não usar os JSON finais como fixtures de testes da busca. Os testes do validador usam conjuntos sintéticos; a integração da busca usa somente um termo de desenvolvimento para verificar referências, sem estimar qualidade.
- As vinte consultas finais serão executadas para comparar métodos somente no M4. Qualquer ajuste motivado por resultados finais será identificado como exploração posterior, conforme o plano.

## Situação e esforço

Na preparação inicial: 30 propostas, zero aprovações humanas registradas, nenhuma métrica de qualidade calculada. A busca literal e a validação estrutural estão prontas para uso, mas M2 não será declarado concluído enquanto a revisão humana estiver pendente.

O autor pode revisar em grupos de IDs. Registre o tempo gasto nessa atividade para reestimar o plano após M2; ainda não há medição do esforço real da revisão. M3 não foi iniciado.
