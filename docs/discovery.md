# Descoberta do projeto

Registro da entrevista iniciada em 25 de outubro de 2026. Este documento distingue decisões aprovadas, observações sobre os dados e escolhas ainda abertas.

## Decisões aprovadas — rodada 1

1. **Direção:** busca documental com análise exploratória de apoio. O acervo literário será uma demonstração de competências para trabalho freelancer em paralelo ao emprego atual.
2. **Disponibilidade de referência:** quatro horas semanais durante seis semanas. Não é uma estimativa validada de entrega; o escopo depende da inspeção dos arquivos.
3. **Aprendizado:** aproveitar a experiência em Python e análise de dados, concentrando o aprendizado em NLP e avaliação de busca.
4. **Organização:** manter um repositório próprio, separado do repositório de perfil, e registrar glossário e decisões durante a descoberta.

O usuário autorizou a criação do repositório no GitHub e informou que fará a atualização do notebook no Kaggle. A publicação de um notebook não foi executada por esta etapa.

## Decisões aprovadas — rodada 2

5. **Situação de uso:** demonstrar como pequenas equipes podem localizar informações em acervos de documentos, usando Sherlock Holmes como exemplo público. Isso não representa validação em documentos empresariais.
6. **Idiomas:** consultas em inglês na primeira versão; interface e relatório em português; resumo do projeto em inglês. Busca multilíngue fica para uma possível evolução.
7. **Dashboard:** usar Streamlit, aproveitando a experiência já presente no portfólio e concentrando o aprendizado em NLP.
8. **Avaliação humana:** reservar parte do projeto para o autor revisar cerca de 20–30 consultas e seus trechos relevantes. A quantidade final e os critérios de avaliação dependem da inspeção dos textos.

Estas quatro decisões foram aprovadas pelo usuário em 25 de outubro de 2026. O escopo funcional e os critérios de conclusão continuam em discussão.

## Decisões aprovadas — rodada 3

9. **Resultados da busca:** retornar até cinco trechos, mostrando título da obra, arquivo e localização verificável. Incluir filtro por obra e mensagem quando não houver correspondência. Geração de respostas e chatbot ficam fora da primeira versão.
10. **Métodos comparados:** busca literal por palavras ou expressões e busca por relevância usando TF-IDF. A comparação será reproduzível e apoiada na avaliação humana; não foi assumida superioridade de um método.
11. **Análise exploratória:** limitar a análise de apoio ao tamanho dos textos, termos frequentes e qualidade da preparação dos dados.
12. **Dados fora do Git:** manter os textos originais fora do repositório, documentando a obtenção no Kaggle e a identificação do arquivo utilizado. Versionar código, documentação e avaliação; anexar o corpus como entrada do notebook Kaggle e documentar sua origem no relatório.

Estas quatro decisões foram aprovadas pelo usuário em 25 de outubro de 2026. A regra de segmentação, o protocolo final de avaliação e os detalhes de publicação continuam abertos.

## Decisões aprovadas — rodada 4

13. **Unidade de busca:** começar com parágrafos, preservando arquivo e intervalo de linhas de origem para conferir cada resultado. A identificação completa de capítulos e contos fica para uma possível evolução.
14. **Avaliação:** preparar 30 consultas, sendo dez para desenvolvimento e vinte para avaliação final, incluindo consultas sem resposta no corpus. Reservar as vinte finais para depois de fechar os ajustes. Comparar consultas que encontram trecho relevante entre os cinco resultados e consultas sem resposta que recebem resultados indevidos.
15. **Publicação:** planejar o dashboard no Streamlit Community Cloud e o relatório no GitHub Pages. Aplicativos inativos no Community Cloud podem hibernar e precisar de reativação ao acessar.
16. **Ordem de entrega:** processamento e busca → notebook Kaggle e avaliação → relatório Quarto → dashboard Streamlit, reaproveitando a mesma lógica Python.

Estas quatro decisões foram aprovadas pelo usuário em 25 de outubro de 2026. O usuário pediu a consolidação do plano e dos marcos para confirmação final antes da implementação.

## Entregas solicitadas

- Python como linguagem do projeto.
- Notebook Jupyter para o Kaggle.
- Relatório em Quarto para GitHub Pages.
- Dashboard posterior em Streamlit.

A proposta é compartilhar o processamento entre as entregas; a organização técnica ainda depende da definição do escopo.

## Observações verificadas no dataset

Fonte: [página pública do Kaggle](https://www.kaggle.com/datasets/talesgomes27/sherleck-books), consultada pelo navegador integrado em 25 de outubro de 2026.

- Título: Sherlock Holmes Series.
- Versão exibida: 3.
- Explorador: nove arquivos TXT, 4,04 MB no total.
- A descrição lista apenas seis obras, divergindo do inventário de arquivos.
- A prévia de `a_study_in_scarlet.txt` informa inglês, UTF-8 e Project Gutenberg, além de mostrar cabeçalhos e notas editoriais. Isso ainda não foi verificado nos demais arquivos.
- Licença exibida pelo Kaggle: “Other (specified in description)”. Não foi concluída a verificação das condições de cada arquivo.

Inventário visível:

```text
a_study_in_scarlet.txt
his_last_bow.txt
the_adventures_of_sherlock_holmes.txt
the_case-book_of_sherlock_holmes.txt
the_hound_of_the_baskervilles.txt
the_memoirs_of_sherlock_holmes.txt
the_return_of_sherlock_holmes.txt
the_sign_of_the_four.txt
the_valley_of _fear.txt
```

O espaço em `the_valley_of _fear.txt` reproduz o nome mostrado no explorador e foi posteriormente confirmado no ZIP, conforme a inspeção abaixo.

### Inspeção do arquivo baixado

Em 25 de outubro de 2026, o [endpoint público oficial de download do Kaggle](https://www.kaggle.com/api/v1/datasets/download/talesgomes27/sherleck-books) retornou um ZIP com os nove arquivos do inventário. A inspeção foi feita em diretório temporário, sem adicionar o corpus ao repositório.

- ZIP: 1.514.187 bytes; soma dos arquivos descompactados: 4.041.127 bytes.
- SHA-256 do ZIP: `5abf2fe7bc636289347c2da51a7b611bda39ed451543c6428f79215328eeaaa3`.
- Os nove arquivos começam com BOM UTF-8, confirmado pelos bytes `EF BB BF`, e decodificam com UTF-8-SIG.
- Os nove arquivos têm separações por linhas em branco após normalizar quebras de linha. Essa observação fundamentou a escolha de parágrafos na decisão 13; os vínculos com linhas do arquivo de origem devem ser preservados durante a implementação.
- A inspeção encontrou formatos variados de capítulos e títulos de contos. Identificar automaticamente todos esses títulos ainda não está garantido.
- O nome `the_valley_of _fear.txt`, incluindo o espaço, foi confirmado dentro do ZIP.

O endpoint usado não fixa uma versão no endereço. O hash identifica exatamente o arquivo inspecionado; não é uma garantia de que um download futuro retornará os mesmos bytes. A inspeção estrutural não conclui a verificação das condições de redistribuição.

## Consolidação e confirmação final

As decisões Q1–Q16 estão aprovadas. O [plano consolidado](plan.md) organiza essas decisões em seis marcos e descreve os detalhes técnicos propostos para executá-las. Esses detalhes e a distribuição de esforço aguardam confirmação final do usuário; a implementação não começou.

Pontos a resolver durante a execução, sem reabrir as escolhas de produto:

- Preparar e revisar as 30 consultas e seus rótulos, separando desenvolvimento e avaliação final antes dos ajustes.
- Definir a regra de abstenção da busca TF-IDF com as dez consultas de desenvolvimento e congelá-la antes da avaliação final.
- Verificar a identificação dos dados por arquivo no Kaggle e as condições de uso e atribuição aplicáveis à exibição pública de trechos.
- Verificar acesso aos destinos de publicação e registrar as URLs apenas depois de testar as entregas publicadas.

## Restrições de interpretação

O corpus serve para demonstrar um fluxo de trabalho, não para afirmar eficácia em documentos empresariais. Não serão apresentados ganhos de tempo, qualidade ou dinheiro sem medição apropriada.

## Referências de publicação

- [Kaggle Notebooks](https://www.kaggle.com/docs/notebooks): o dataset pode ser anexado como entrada do notebook, sem incluir credenciais no código.
- [Quarto e GitHub Pages](https://quarto.org/docs/publishing/github-pages.html): publicação do relatório estático.
- [Implantação de dashboards Quarto](https://quarto.org/docs/dashboards/deployment.html): distinção entre saída estática e aplicações com servidor.
- [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud): destino aprovado para a demonstração interativa.

Os destinos aprovados são GitHub Pages para o relatório e Streamlit Community Cloud para a aplicação Python. Nenhuma dessas entregas foi implantada ainda.
