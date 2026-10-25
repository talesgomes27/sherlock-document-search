# Descoberta do projeto

Registro da entrevista iniciada em 25 de outubro de 2026. Este documento distingue decisões aprovadas, observações sobre os dados e escolhas ainda abertas.

## Decisões aprovadas — rodada 1

1. **Direção:** busca documental com análise exploratória de apoio. O acervo literário será uma demonstração de competências para trabalho freelancer em paralelo ao emprego atual.
2. **Disponibilidade de referência:** quatro horas semanais durante seis semanas. Não é uma estimativa validada de entrega; o escopo depende da inspeção dos arquivos.
3. **Aprendizado:** aproveitar a experiência em Python e análise de dados, concentrando o aprendizado em NLP e avaliação de busca.
4. **Organização:** manter um repositório próprio, separado do repositório de perfil, e registrar glossário e decisões durante a descoberta.

O usuário autorizou a criação do repositório no GitHub e informou que fará a atualização do notebook no Kaggle. A publicação de um notebook não foi executada por esta etapa.

## Entregas solicitadas

- Python como linguagem do projeto.
- Notebook Jupyter para o Kaggle.
- Relatório em Quarto para GitHub Pages.
- Dashboard posterior em Streamlit ou Shiny.

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

O espaço em `the_valley_of _fear.txt` reproduz o nome mostrado no explorador; ainda não foi comparado a um download.

## Decisões abertas — próxima rodada

- Público e situação de uso que a demonstração pretende atender.
- Idioma das consultas e dos materiais públicos.
- Limites funcionais da primeira versão: tipos de busca, filtros, apresentação de resultados e eventual geração de respostas.
- Como construir a avaliação e definir critérios de conclusão.
- Granularidade dos resultados, após inspeção da estrutura dos textos.
- Streamlit ou Shiny e destino de hospedagem do dashboard.
- Organização do código compartilhado e execução do notebook no ambiente Kaggle.

## Restrições de interpretação

O corpus serve para demonstrar um fluxo de trabalho, não para afirmar eficácia em documentos empresariais. Não serão apresentados ganhos de tempo, qualidade ou dinheiro sem medição apropriada.

## Referências de publicação

- [Kaggle Notebooks](https://www.kaggle.com/docs/notebooks): o dataset pode ser anexado como entrada do notebook, sem incluir credenciais no código.
- [Quarto e GitHub Pages](https://quarto.org/docs/publishing/github-pages.html): publicação do relatório estático.
- [Implantação de dashboards Quarto](https://quarto.org/docs/dashboards/deployment.html): distinção entre saída estática e aplicações com servidor.

O relatório e a aplicação Python devem ter estratégias de publicação próprias. Hospedagem do dashboard ainda não foi definida.
