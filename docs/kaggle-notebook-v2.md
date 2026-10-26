# Notebook Kaggle próprio da v2

Para leitura e importação no Kaggle, use a [edição de apresentação v2](../notebooks/portfolio/sherlock_document_search_v2.ipynb), com linguagem revisada e uma matriz por consulta. Os detalhes abaixo registram a validação do notebook original; veja os [limites da verificação editorial](editorial-presentation.md).

O autor aprovou a v2 e autorizou este notebook em 25 de outubro de 2026. O arquivo [sherlock_document_search_v2.ipynb](../notebooks/sherlock_document_search_v2.ipynb) reúne busca literal, TF-IDF e BM25, gráficos, resultados por consulta e análise das negativas. O notebook v1 e seus auxiliares foram preservados.

## Executar no Kaggle

1. Importe `sherlock_document_search_v2.ipynb` como um novo notebook na sua conta.
2. Anexe o dataset [Sherlock Holmes Series](https://www.kaggle.com/datasets/talesgomes27/sherleck-books). São esperados os mesmos nove TXT identificados pelos hashes do corpus original.
3. Habilite Internet para instalar ferramentas, Python gerenciado e dependências quando ausentes do cache.
4. Reinicie o kernel e execute todas as células na ordem.
5. Confira os gráficos, as tabelas das 18 positivas e seis negativas e os primeiros IDs/scores retornados nas negativas.
6. Salve uma versão executada. Os arquivos para download ficam em `sherlock_analysis_v2` na área Output: `search_results.json` e quatro figuras PNG/SVG em `figures/`.

O notebook inclui seu código e metadados; não clona nem baixa código do projeto. O corpus é a entrada anexada. Nenhum token ou conta adicional é necessário ao código. A publicação ou atualização na conta Kaggle é uma ação do autor; a entrega local não confirma execução ou publicação na plataforma.

## Conteúdo e interpretação

O primeiro gráfico mostra palavras retidas nas nove obras. O segundo compara os três métodos no mesmo teste de 18 positivas e seis negativas. As medidas contam consultas com pelo menos uma referência conhecida no top 5 e consultas negativas com algum retorno. Os denominadores não são parágrafos únicos; as referências não são exaustivas e um hit pode ser evidência parcial.

Os resultados permanecem literal 6/18 e 0/6; TF-IDF 10/18 e 6/6; BM25 12/18 e 6/6. O notebook reproduz a avaliação congelada, sem grades ou novos ajustes. Scores de métodos diferentes não são comparáveis entre si nem probabilidades de resposta.

A seção das seis negativas explica como correspondências lexicais podem recuperar texto relacionado sem informar idade, preço, tarifa, nome, peso ou calibre pedidos. Há IDs e scores para rastrear o resultado, sem republicar trechos dos livros. O [diagnóstico detalhado](v2-no-answer-analysis.md) documenta os seis casos e hipóteses para outro ciclo; nenhuma nova regra de abstenção foi implementada.

## Código incluído e ambiente

O gerador `scripts/build_kaggle_v2_bundle.py` confere os 48 arquivos do snapshot v2 e o relatório de referência antes de montar o ZIP determinístico. Inclui também os artefatos históricos que o verificador de preservação da v1 exige, sem alterá-los. O único arquivo em `data/` dentro do bundle é o JSON aprovado das consultas finais, já publicado, obtido da cópia pública byte-idêntica; o bundle não depende dos arquivos locais de revisão nem contém os TXT.

A execução extrai o código em uma pasta própria, instala uv 0.13.5 e provisiona Python 3.11.17 com o lockfile existente. O processamento fica separado do kernel de gráficos. Matplotlib usa o ambiente do kernel; quando ausente, a célula instala a versão usada na validação. O payload pode ser recolhido por interfaces que respeitem a metadata Jupyter; não é necessário editá-lo para executar.

O avaliador grava primeiro em `analysis/reports/v2/notebook_execution.json`, dentro da área permitida por sua proteção de saídas. O notebook compara esses bytes com o relatório incluído e copia o resultado para `search_results.json`. Arquivos congelados não são sobrescritos. Pastas conflitantes e links nas saídas são recusados.

## Validação local

Foram executadas oito células em kernel novo, sem erros, com dois gráficos inline e quatro arquivos de figura. O JSON foi idêntico byte a byte ao relatório final aprovado, SHA-256 `4c05fc86dcd6907bfafec5283b45c5e66ae91aaf3ef323466b54f179039ac92b`. As figuras foram inspecionadas visualmente. A revisão independente não encontrou achados acionáveis no notebook ou no empacotamento. Os 106 testes passaram com os dados reais, sem ignorados; os 35 ativos v1 e 48 arquivos congelados v2 permanecem intactos.

A [evidência do notebook](../reports/v2/notebook_validation.json) registra explicitamente que o kernel é local, não Kaggle. A única normalização posterior de apresentação recolhe a célula de payload por metadata: fontes e outputs executados permanecem iguais. A execução real nesta plataforma ainda não foi conferida.

## Reproduzir a verificação e manter o arquivo

Use um ambiente separado com as [ferramentas de notebook existentes](../notebooks/validation-requirements.txt), sem alterar pyproject ou lockfile:

```bash
uv venv --python 3.11.17 /tmp/sherlock-notebook-v2-validation
uv pip install --python /tmp/sherlock-notebook-v2-validation/bin/python -r notebooks/validation-requirements.txt
/tmp/sherlock-notebook-v2-validation/bin/python scripts/validate_notebook_v2.py \
  --notebook notebooks/sherlock_document_search_v2.ipynb \
  --raw-dir data/raw \
  --expected-report reports/v2/final.json \
  --output-dir /tmp/sherlock-notebook-v2-run
```

A saída precisa ser uma pasta nova. O validador limpa outputs apenas da cópia em memória, executa em kernel separado, verifica fontes, sequência, figuras e igualdade do relatório. O resultado executado e sua evidência ficam nessa pasta; entradas são preservadas.

Após mudança autorizada nos dados incluídos, o gerador atualiza somente o notebook v2 e limpa seus outputs. Antes de atualizar qualquer ativo congelado, é preciso outro protocolo de experimento; o gerador recusa fontes divergentes.

```bash
uv run python scripts/build_kaggle_v2_bundle.py --check
```

O comando sem `--check` reescreve o payload, após conferir as fontes; em seguida, execute a validação e confira a cópia executada antes de publicá-la. Os scripts e o notebook da v1 são separados e continuam preservados.
