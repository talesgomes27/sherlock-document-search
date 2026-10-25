# Execução — Sherlock Document Search

## Autorização e escopo

Em 25 de outubro de 2026, o usuário confirmou o plano e autorizou iniciar M1: “Confirmo o plano e autorizo iniciar o M1. Siga o recomendado, utilizando subagentes quando for benéfico.”

Arquétipo A — dados, análise e Quarto, identificado pelo escopo explícito do [plano aprovado](docs/plan.md). Condução contínua dentro do M1 autorizado; M2–M6 não foram iniciados. A criação e manutenção do repositório GitHub fazem parte do contexto autorizado desta conversa; nenhum deploy de aplicação está incluído neste marco.

Linha de base: repositório limpo, apenas documentação de planejamento, sem pacote, testes ou manifests de implementação. Não havia suíte preexistente a executar nem dados originais versionados.

## Estado do M1

Implementado e validado tecnicamente; aceite do usuário pendente. O trabalho está restrito à preparação, rastreabilidade e análise inicial de limpeza.

| Gate da execução | Evidência no M1 |
|---|---|
| Núcleo e contratos | Pacote Python sem dependências de execução; hashes e inventário estritos; parágrafos com linhas originais; dez testes incluindo regressões. |
| Integração e execução | Download público pelo código, nove TXT preparados e conferência de todos os 15.598 parágrafos contra as linhas de origem. |
| Apresentação e saídas | JSONL local com referências e JSON numérico de qualidade; nenhum dashboard ou figura era necessário ao M1. |
| Documentação | README, preparação, proveniência, manifesto e relatório numérico alinhados à execução. |
| Revisão integrada e build | Revisão independente, correção de dois achados, testes completos, sdist/wheel e instalação isolada com comparação das saídas. |

## Verificações executadas

- Antes da implementação, os testes falharam por ausência do módulo esperado. Depois, os testes sintéticos passaram e a integração real foi executada.
- `python -m sherlock_search --download`: obtenção pública validada por tamanho/hash do ZIP e dos nove TXT.
- `python -m unittest discover -s tests -v`: dez testes passaram com o corpus real, incluindo roundtrip de cada parágrafo.
- `uv build`: sdist e wheel construídos. Wheel instalado em ambiente Python 3.11.17 isolado, sem dependências de execução.
- Testes com o pacote instalado e execução da CLI fora da árvore do código-fonte; relatório e JSONL comparados byte a byte com a execução pelo código-fonte.
- Casos de erro da CLI conferidos: pasta de origem ausente, origem igual à saída e tentativa de repetir download sobre pasta existente; todos encerraram com mensagem clara, sem traceback nem escrita indevida.
- Verificação de diff e de exclusão dos dados no Git antes da entrega.

Ambientes de verificação: Linux; suíte completa em Python 3.15.0 pelo código-fonte e Python 3.11.17 pelo pacote instalado. Não foram testados Kaggle, Windows, macOS, GitHub Pages ou Community Cloud neste marco.

## Revisão e delegação

Dois subagentes com modelo mais leve inspecionaram proveniência e fronteiras editoriais. O agente principal conferiu limites, hashes e os resultados produzidos. Um terceiro subagente fez revisão independente de implementação e testes.

A revisão identificou dois marcadores `THE END` retidos e uma fração Unicode contada como palavra. Ambos foram corrigidos com testes de regressão; a revisão das correções não encontrou novos achados.

## Pendências e próximo marco

- As condições de uso e atribuição para publicar trechos ainda precisam ser verificadas; isso não impediu a preparação local nem a publicação de metadados e contagens.
- A limpeza mantém notas internas e alguns títulos editoriais. Não se implementou parser geral de capítulos ou contos.
- A revisão humana das 30 consultas é tarefa do M2 e ainda não começou. As vinte consultas finais não foram criadas nem utilizadas para ajustes.
- O próximo ponto de reestimativa do esforço será após a revisão humana em M2; a referência de 24 horas não foi convertida em garantia de prazo.
- Após o aceite do M1 e a autorização para o M2, preparar as consultas e a busca literal conforme o plano. Não iniciar automaticamente marcos posteriores.

## Correção da pasta local

O usuário indicou `sherlock_holmes_series/` como pasta local do projeto. O checkout foi consolidado nessa pasta, preservando o histórico Git e os nove TXT que já existiam diretamente em `data/`. Seus hashes coincidem com o snapshot do M1. Esses TXT também ficam ignorados pelo Git; a cópia preparada continua em `data/raw/` e `data/processed/`. O ambiente virtual foi recriado no novo caminho para evitar referências ao local anterior.
