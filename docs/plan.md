# Plano e marcos — Sherlock Document Search

Status: plano confirmado pelo usuário em 25 de outubro de 2026, com autorização para iniciar M1. O M1 foi aprovado pelo usuário. O M2 foi autorizado e concluído, com busca literal validada e as 30 consultas aprovadas pelo autor. O M3 foi autorizado e concluído com ajuste somente em desenvolvimento; O M4 foi autorizado e está em andamento; M5–M6 ainda não começaram. Este documento consolida o [registro de descoberta](discovery.md), sem substituí-lo.

## Objetivo e entrega

Demonstrar como pequenas equipes podem localizar informações em acervos documentais, usando os textos de Sherlock Holmes como exemplo público. O projeto demonstrará preparação de dados textuais, comparação de métodos de busca, avaliação humana e comunicação de resultados para um portfólio de serviços freelancer.

O resultado será um núcleo Python, um notebook Jupyter para o Kaggle, um relatório Quarto no GitHub Pages e um dashboard Streamlit no Community Cloud. O autor fará a publicação e a atualização do notebook no Kaggle. As consultas serão em inglês, a interface e o relatório em português e haverá um resumo do projeto em inglês.

O corpus literário não comprova desempenho em documentos empresariais ou retorno comercial. Não será afirmada superioridade de um método sem os resultados da avaliação.

## Escopo aprovado

- Usar os nove arquivos TXT do dataset [Sherlock Holmes Series](https://www.kaggle.com/datasets/talesgomes27/sherleck-books), mantendo os originais fora do Git.
- Usar parágrafos como unidade inicial de busca, com título da obra, nome do arquivo e intervalo de linhas do arquivo-fonte.
- Comparar busca literal por palavras ou expressões com busca por relevância TF-IDF.
- Retornar até cinco resultados, permitir filtro por obra e apresentar mensagem quando não houver correspondência pela regra de cada método.
- Limitar a análise exploratória a tamanho dos textos, termos frequentes e qualidade da preparação dos dados.
- Avaliar 30 consultas com revisão humana: dez para desenvolvimento e vinte para avaliação final, incluindo consultas sem resposta.

Não fazem parte da primeira versão: chatbot, geração de respostas, busca multilíngue e identificação completa de capítulos e contos.

## Detalhes técnicos aprovados para executar as decisões

Estes detalhes foram confirmados com o plano. A preparação e o empacotamento do M1 e a busca literal do M2 foram implementados e testados. Os rótulos do M2 foram aprovados. O TF-IDF, a regra de abstenção e o congelamento do M3 estão implementados; M4–M6 continuam pendentes. Consulte as evidências em [task.md](../task.md).

**Dados e rastreabilidade.** Preservar os arquivos recebidos, tratar UTF-8 com BOM e quebras de linha, e remover material editorial da análise sem perder a ligação com as linhas de origem. Registrar tamanho e SHA-256 por TXT; guardar também o hash do ZIP quando disponível. O Kaggle fornece os TXT como entrada, portanto a reprodução não dependerá de receber o mesmo ZIP. Alterações inesperadas nos arquivos devem produzir aviso claro e exigir verificação antes da comparação de resultados.

**Busca e ausência de correspondência.** A busca literal procurará palavras completas ou a expressão informada, sem diferenciar maiúsculas e minúsculas. Ordenará os candidatos pela contagem de ocorrências, com desempate determinístico por arquivo e linha. TF-IDF usará similaridade de cosseno para ordenar parágrafos e uma regra explícita para não retornar candidatos inadequados. A regra e eventuais limiares serão ajustados somente nas dez consultas de desenvolvimento e congelados antes da avaliação final. Pontuação de similaridade não será apresentada como probabilidade de a resposta estar correta. Consultas vazias ou compostas apenas por termos não representados não devem provocar erro nem resultados arbitrários.

**Código compartilhado e notebook.** Manter um pequeno pacote Python para preparação, busca e avaliação, importado pelo notebook, pelo relatório e pelo dashboard. O notebook Kaggle usará o corpus anexado como entrada e instalará o pacote do repositório público em um commit fixo; essa proposta exige Internet habilitada na instalação e não inclui credenciais no notebook. A versão de código e as dependências usadas serão registradas. O notebook deverá funcionar após reiniciar o ambiente e executar as células na ordem.

**Dados na aplicação hospedada.** Obter o corpus da fonte original, validar a identificação esperada e reutilizá-lo em cache durante a execução. Se o download falhar ou os dados divergirem, exibir mensagem compreensível em vez de apresentar métricas ou resultados como se a reprodução estivesse validada. O cache do serviço não será tratado como armazenamento permanente. Os TXT e índices que reproduzam o corpus não serão enviados ao Git.

**Análise de apoio.** Documentar a regra de contagem de palavras e o tratamento dos termos frequentes. Comparar proporções quando os tamanhos dos textos forem diferentes e mostrar o efeito da remoção de cabeçalhos e notas editoriais. Não tratar datas, nomes de personagens ou assuntos como campos estruturados já disponíveis.

## Avaliação proposta

1. Preparar 30 consultas em inglês com participação do autor, abrangendo arquivos distintos, consultas por palavras e expressões e casos sem resposta. Registrar a divisão antes dos ajustes: dez de desenvolvimento e vinte finais. Ambos os grupos devem incluir casos sem resposta; as quantidades por tipo serão documentadas antes da execução.
2. Para consultas com resposta, registrar trechos relevantes conhecidos por arquivo e linhas. Para negativas, documentar a revisão que sustenta a ausência de uma resposta no corpus. Esses rótulos são uma avaliação curada e limitada, não uma prova de que todos os trechos relevantes foram identificados.
3. Durante desenvolvimento, usar somente as dez consultas permitidas para ajustar limpeza, regras da busca e limiar de abstenção. Manter as vinte finais sem uso para ajustes.
4. Fixar a versão do código, do corpus e dos rótulos antes da avaliação final. Comparar os métodos sobre as mesmas consultas e os mesmos parágrafos.
5. Nas consultas com resposta, registrar a fração que recupera ao menos um trecho relevante entre os cinco primeiros resultados. Nas consultas sem resposta, registrar a fração em que o sistema retorna algum resultado indevido. Informar também os numeradores e denominadores, os casos individuais e as falhas observadas.
6. Publicar o resultado observado, mesmo que TF-IDF não supere a busca literal. Se os resultados finais motivarem novos ajustes, identificá-los como exploração posterior, sem apresentar uma nova medição no mesmo conjunto como avaliação independente.

O critério de conclusão é entregar uma comparação reproduzível, com rastreabilidade e análise dos erros. Não há meta numérica de qualidade validada nem promessa de desempenho para clientes.

## Seis marcos de referência

A disponibilidade aprovada é de quatro horas semanais por seis semanas, totalizando 24 horas de referência. A distribuição abaixo é uma proposta de esforço do autor, incluindo revisão humana e validação guiada; não é uma garantia de prazo. Ao concluir M1, conferir se a preparação e o acesso aos ambientes confirmam a estimativa. Reestimar após M2 com o esforço real da revisão humana e conferir novamente a disponibilidade e os acessos antes de M4 e M6. Qualquer revisão de prazo ou escopo deve ficar registrada, sem omitir critérios de conclusão.

| Marco | Referência | Entrega e evidência de conclusão |
|---|---|---|
| M1 — Dados e preparação | Semana 1 · 4 h | Obtenção dos nove TXT documentada, identificação por arquivo registrada, parágrafos ligados às linhas originais e análise inicial de limpeza. Testes conferem essa ligação em exemplos e a leitura dos nove arquivos. Registrar proveniência, atribuição e eventuais pendências de uso antes da publicação de trechos. |
| M2 — Consultas e busca literal | Semana 2 · 4 h | Autor revisa as 30 consultas e os rótulos; separar dez de desenvolvimento e vinte finais antes dos ajustes. Busca literal e filtro por obra funcionam, respeitando o limite de cinco e a ausência de correspondência. Testes usam exemplos sintéticos e o conjunto de desenvolvimento. |
| M3 — TF-IDF e comparação de desenvolvimento | Semana 3 · 4 h | TF-IDF compartilha a mesma preparação e as mesmas referências. Regra de abstenção definida com as dez consultas de desenvolvimento, testes de entradas vazias e termos ausentes e comportamento de desempate verificado. Congelar código e parâmetros antes da avaliação final. |
| M4 — Notebook e avaliação final | Semana 4 · 4 h | Notebook executa do início ao fim em ambiente Kaggle limpo, com pacote em commit fixo e corpus anexado. Avaliação das vinte consultas finais gera resultados por consulta e métricas dos dois métodos. Autor publica ou atualiza o notebook e informa a URL. |
| M5 — Relatório Quarto | Semana 5 · 4 h | Relatório reproduz resultados de M4, descreve limpeza, métodos, erros e limitações, e inclui resumo em inglês. Renderização HTML concluída e publicação no Pages verificada por abertura da URL e inspeção de figuras e links. |
| M6 — Dashboard e entrega | Semana 6 · 4 h | Streamlit permite consulta, filtro e comparação dos dois métodos com referências de origem. Testar consulta com resultado, sem resultado, vazia, filtro e falha de obtenção dos dados. Publicar no Community Cloud, verificar a URL e reunir os links e instruções no README. |

M2 depende dos dados preparados em M1. M3 usa somente as consultas de desenvolvimento de M2. M4 depende da revisão humana e do congelamento de M3. M5 e M6 usam os resultados e a versão de código registrados em M4; não introduzem ajustes de busca guiados pela avaliação final.

## Responsabilidades e validação

O agente implementará o código e os testes focados nas regras de preparação, busca, filtros, localização e avaliação; preparará o notebook, o relatório e o dashboard e verificará as entregas nos ambientes disponíveis. Tarefas factuais, inspeções delimitadas e revisões poderão ser delegadas a subagentes com modelo mais leve quando suficiente; a integração dos resultados permanece sob responsabilidade do agente principal.

O autor revisará a relevância das consultas e as situações sem resposta, publicará ou atualizará o notebook Kaggle e realizará os passos de autenticação ou conexão que exigirem sua participação. O plano não presume que acesso ao GitHub já conceda acesso ao Kaggle ou ao Community Cloud.

Executar os testes pertinentes ao código, a execução completa do notebook, a renderização Quarto e as verificações das URLs antes de declarar cada entrega concluída. As verificações do M1 estão registradas em [task.md](../task.md). A busca literal do M2 também foi testada. As verificações de TF-IDF, calibração de desenvolvimento e congelamento do M3 foram concluídas. Notebook, avaliação final, relatório e aplicação continuam reservados aos respectivos marcos.

## Dependências e limites conhecidos

- As condições de uso e atribuição dos arquivos ainda precisam ser verificadas para a exibição pública de trechos. Manter os dados fora do Git não resolve sozinho essa pendência.
- A fonte de download e os serviços de hospedagem podem estar indisponíveis; o hash identifica o corpus inspecionado, mas não garante sua disponibilidade futura.
- O notebook proposto depende de Internet para instalar o pacote do GitHub em commit fixo. Essa condição deve estar visível nas instruções e ser verificada em M4.
- O Community Cloud pode hibernar aplicativos inativos. A demonstração não inclui compromisso de disponibilidade de um serviço de produção.
- Trinta consultas constituem uma avaliação pequena e curada. Os resultados não devem ser generalizados como desempenho em outros acervos.
- A revisão humana, a configuração dos destinos e a preparação do corpus podem exigir rever a estimativa de 24 horas. As revisões de esforço ocorrerão em M1, após a anotação de M2 e antes de M4 e M6.

## Confirmação e execução

Em 25 de outubro de 2026, o usuário confirmou o plano e autorizou iniciar M1. O M1 foi implementado, validado tecnicamente e aprovado pelo usuário, conforme [task.md](../task.md). O M2 foi autorizado e concluído, com as 30 consultas aprovadas no chat. O M3 foi autorizado e concluído, conforme as evidências em task.md. O M4 foi autorizado e está em andamento; M5–M6 não foram iniciados; notebook, relatório Quarto e dashboard ainda não foram publicados.
