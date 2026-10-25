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
- Os nove arquivos têm separações por linhas em branco após normalizar quebras de linha. Isso permite propor trechos baseados em parágrafos; a regra final de segmentação ainda não foi aprovada.
- A inspeção encontrou formatos variados de capítulos e títulos de contos. Identificar automaticamente todos esses títulos ainda não está garantido.
- O nome `the_valley_of _fear.txt`, incluindo o espaço, foi confirmado dentro do ZIP.

O endpoint usado não fixa uma versão no endereço. O hash identifica exatamente o arquivo inspecionado; não é uma garantia de que um download futuro retornará os mesmos bytes. A inspeção estrutural não conclui a verificação das condições de redistribuição.

## Decisões abertas — próxima rodada

- Regra de segmentação e referências que permitam localizar cada trecho no arquivo de origem.
- Protocolo da avaliação humana: separação entre desenvolvimento e avaliação final, consultas sem resposta e critérios de conclusão.
- Destino de hospedagem do dashboard Streamlit.
- Organização do código compartilhado e reprodução do notebook no ambiente Kaggle.
- Procedimento de obtenção e identificação dos dados para execução local e hospedada, respeitando a decisão de manter o corpus original fora do Git.
- Ordem de entrega e confirmação final do entendimento antes da implementação.

## Restrições de interpretação

O corpus serve para demonstrar um fluxo de trabalho, não para afirmar eficácia em documentos empresariais. Não serão apresentados ganhos de tempo, qualidade ou dinheiro sem medição apropriada.

## Referências de publicação

- [Kaggle Notebooks](https://www.kaggle.com/docs/notebooks): o dataset pode ser anexado como entrada do notebook, sem incluir credenciais no código.
- [Quarto e GitHub Pages](https://quarto.org/docs/publishing/github-pages.html): publicação do relatório estático.
- [Implantação de dashboards Quarto](https://quarto.org/docs/dashboards/deployment.html): distinção entre saída estática e aplicações com servidor.

O relatório e a aplicação Python devem ter estratégias de publicação próprias. Hospedagem do dashboard ainda não foi definida.
