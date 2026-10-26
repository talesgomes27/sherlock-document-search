# M4 — notebook e avaliação final

Para leitura e importação no Kaggle, use a [edição de apresentação v1](../notebooks/portfolio/sherlock_document_search_v1.ipynb), com linguagem revisada e uma matriz por consulta. Os detalhes abaixo registram a validação do notebook original; veja os [limites da verificação editorial](editorial-presentation.md).

O M4 preparou o notebook para o Kaggle e avaliou as vinte consultas finais com os métodos congelados no M3. A versão reformulada descrita aqui foi validada em kernel local limpo, com dois gráficos e tabelas por consulta; a execução atual na plataforma Kaggle ainda não foi conferida. O autor aprovou essa execução em 25 de outubro de 2026. Nenhum parâmetro, rótulo, recorte do corpus ou código congelado foi alterado após observar os resultados finais.

## Arquivos entregues

- [Notebook para importar no Kaggle](../notebooks/sherlock_document_search.ipynb).
- [Relatório final completo](../reports/m4_final.json), com os IDs e scores de cada consulta, sem textos dos livros.
- [Evidência da execução local do notebook](../reports/m4_notebook_validation.json).
- [Ferramentas externas de validação](../notebooks/validation-requirements.txt); elas não alteram o pyproject ou o lockfile do modelo.

## Como executar no Kaggle

1. Importe o arquivo `sherlock_document_search.ipynb` em um notebook Kaggle.
2. Anexe o dataset [Sherlock Holmes Series](https://www.kaggle.com/datasets/talesgomes27/sherleck-books). O snapshot esperado corresponde aos nove TXT identificados no M1, na versão 3 exibida durante a descoberta. Os hashes, e não somente o número da versão, são a referência de integridade.
3. Habilite Internet para instalar `uv`, o Python gerenciado e dependências que não estejam em cache. O notebook não clona o projeto nem baixa seu código.
4. Execute todas as células desde um kernel reiniciado. O notebook extrai o ZIP determinístico de código e metadados embutido no arquivo e localiza o dataset anexado por `a_study_in_scarlet.txt` em `/kaggle/input`; se encontrar zero ou múltiplas cópias, interrompe para que a entrada correta seja selecionada explicitamente.
5. Confira as tabelas e os gráficos no kernel. O JSON fica em `/kaggle/working/sherlock_analysis/search_results.json`; os gráficos PNG e SVG ficam em `/kaggle/working/sherlock_analysis/figures/`.
6. O autor publica ou atualiza o notebook e informa a URL da execução. A publicação não é realizada automaticamente pelo código; a execução atual e sua URL ainda não foram conferidas.

Não inclua tokens ou credenciais no notebook. As fontes e o repositório são públicos; nenhum segredo é necessário ao fluxo computacional.

## Código e ambiente reproduzíveis

O notebook contém um ZIP determinístico com código e metadados, construído a partir de fontes cujos hashes são conferidos contra o snapshot M3. O bundle não contém os TXT do corpus, e o notebook não clona nem baixa código do projeto. O commit `51a69a0264ef318d8506da0a8db627c295a5ccba` pertence ao histórico da implementação anterior, que buscava o código no GitHub; não descreve o fluxo atual.

O kernel usa Python e IPython para apresentação, além de Matplotlib para gerar os gráficos diretamente no kernel. `uv` instala o Python de processamento 3.11.17 e as dependências fixadas pelo `uv.lock`, em ambiente separado do kernel Kaggle. As versões exigidas são:

| Componente | Versão |
|---|---|
| Python do processamento | 3.11.17 |
| scikit-learn | 1.9.1 |
| NumPy | 2.4.6 |
| SciPy | 1.17.1 |

Se o runtime, o corpus ou o código divergir, o avaliador interrompe antes da busca. Os módulos realmente importados também são comparados com o snapshot, evitando conferir uma cópia do código e executar outra. A saída não pode sobrescrever consultas, dados brutos ou arquivos congelados.

O campo `final_queries_executed: false` do arquivo M3 continua inalterado porque descreve o estado histórico daquele snapshot. A execução autorizada do M4 está registrada no relatório final e neste documento; o snapshot não foi reescrito para ocultar sua cronologia.

Fontes de operação: [Kaggle Notebooks](https://www.kaggle.com/docs/notebooks), [KaggleHub](https://github.com/Kaggle/kagglehub), [uv CLI](https://docs.astral.sh/uv/reference/cli/) e [variáveis de ambiente do uv](https://docs.astral.sh/uv/reference/environment/).

## Resultado final observado

| Método | Positivas com trecho conhecido no top 5 | Taxa | Negativas com retorno indevido | Taxa |
|---|---:|---:|---:|---:|
| Literal | 7/16 | 43,75% | 0/4 | 0% |
| TF-IDF | 8/16 | 50% | 4/4 | 100% |

O corte TF-IDF permaneceu em 0,0, sempre excluindo scores iguais a zero. O TF-IDF recuperou uma referência conhecida a mais nas positivas, mas retornou resultados em todas as negativas. Esse conflito não sustenta uma afirmação de superioridade geral.

As referências não são exaustivas, o conjunto é pequeno e suas negativas são anacrônicas. Não encontrar o ID anotado não significa que todos os outros trechos sejam irrelevantes. A avaliação final mede este conjunto aprovado; não comprova desempenho em documentos empresariais. Não se fizeram ajustes para melhorar esses números.

## Validação realizada e etapa pendente

- Os quinze testes sintéticos do novo avaliador foram escritos e revisados antes da primeira execução final real.
- A suíte completa passou com 65 testes, incluindo os dados reais do M1.
- As vinte consultas foram executadas em processo novo, com as versões e o snapshot conferidos antes e depois.
- O notebook atual executou oito células de código em kernel local limpo, sem erros. Gerou dois gráficos inline, quatro arquivos de figura (PNG e SVG) e um relatório idêntico byte a byte ao da primeira avaliação final. O código embutido foi comparado às fontes e os quinze ativos M3 continuam íntegros.
- Os gráficos foram inspecionados visualmente; a revisão independente do empacotamento e da interpretação não encontrou achados acionáveis.
- A revisão independente não identificou achados acionáveis no avaliador ou no bootstrap do notebook.

**A execução e a publicação na plataforma Kaggle ainda não foram conferidas.** A validação local não verifica a autenticação, as permissões de Internet, os anexos ou as condições do runtime hospedado. M5 e M6 não foram iniciados.

## Reproduzir a validação local

As ferramentas Jupyter são instaladas em um ambiente de validação separado:

```bash
uv venv --python 3.11.17 /tmp/sherlock-notebook-validation
uv pip install --python /tmp/sherlock-notebook-validation/bin/python -r notebooks/validation-requirements.txt
/tmp/sherlock-notebook-validation/bin/python scripts/validate_notebook.py \
  --notebook notebooks/sherlock_document_search.ipynb \
  --raw-dir data/raw \
  --expected-report reports/m4_final.json \
  --output-dir /tmp/sherlock-notebook-validation-run
```

Use uma pasta de saída nova. O validador remove outputs apenas da cópia em memória, usa kernel novo, confere a sequência das células e preserva o código do notebook. O notebook executado e o registro JSON ficam na pasta de saída; os arquivos de entrada e o ambiente congelado do projeto são preservados. Esta verificação local foi feita em Linux e não equivale a execução no Kaggle.

## Atualizar o código embutido

`scripts/build_kaggle_bundle.py` gera o ZIP a partir dos quinze ativos congelados, do manifesto e do avaliador. Ele exclui os livros e confere os hashes M3 antes de escrever o payload. Após atualizar código autorizado, regenere e execute o notebook; não copie uma nova implementação dos métodos para suas células.

```bash
python scripts/build_kaggle_bundle.py
python scripts/build_kaggle_bundle.py --check
```

O modo de escrita limpa os outputs do notebook; a validação local produz a cópia executada. Isso preserva uma fonte única para os métodos sem exigir que o leitor do Kaggle acesse o GitHub.
