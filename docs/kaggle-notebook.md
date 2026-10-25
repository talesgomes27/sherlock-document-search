# M4 — notebook e avaliação final

O M4 prepara o notebook para o Kaggle e avalia as vinte consultas finais com os métodos congelados no M3. O autor aprovou essa execução em 25 de outubro de 2026. Nenhum parâmetro, rótulo, recorte do corpus ou código congelado foi alterado após observar os resultados finais.

## Arquivos entregues

- [Notebook para importar no Kaggle](../notebooks/sherlock_document_search.ipynb).
- [Relatório final completo](../reports/m4_final.json), com os IDs e scores de cada consulta, sem textos dos livros.
- [Evidência da execução local do notebook](../reports/m4_notebook_validation.json).
- [Ferramentas externas de validação](../notebooks/validation-requirements.txt); elas não alteram o pyproject ou o lockfile do modelo.

## Como executar no Kaggle

1. Importe o arquivo `sherlock_document_search.ipynb` em um notebook Kaggle.
2. Anexe o dataset [Sherlock Holmes Series](https://www.kaggle.com/datasets/talesgomes27/sherleck-books). O snapshot esperado corresponde aos nove TXT identificados no M1, na versão 3 exibida durante a descoberta. Os hashes, e não somente o número da versão, são a referência de integridade.
3. Habilite Internet. O notebook precisa obter o checkout público, uv, o Python gerenciado e as dependências do lockfile quando não estiverem em cache.
4. Execute todas as células desde um kernel reiniciado. O notebook descobre o diretório a partir de `a_study_in_scarlet.txt` em `/kaggle/input`; se encontrar zero ou múltiplas cópias, interrompe para que a entrada correta seja selecionada explicitamente.
5. Confira as tabelas, o preflight e o postflight. O JSON final fica em `/kaggle/working/sherlock-m4/m4_final.json` para inspeção e download.
6. O autor publica ou atualiza o notebook e informa a URL da execução. A publicação não é realizada automaticamente pelo código.

Não inclua tokens ou credenciais no notebook. As fontes e o repositório são públicos; nenhum segredo é necessário ao fluxo computacional.

## Código e ambiente reproduzíveis

O notebook fixa o commit de suporte `51a69a0264ef318d8506da0a8db627c295a5ccba`, publicado antes da primeira avaliação final real. Esse commit acrescenta o avaliador testado sem modificar os quinze ativos do M3. O snapshot M3 é conferido antes e depois da execução.

O kernel usa apenas Python, IPython e uv 0.13.5 para apresentação e preparação. O processamento roda em outro ambiente, provisionado com `uv sync --managed-python --python 3.11.17 --frozen`, sem trocar as bibliotecas numéricas já carregadas pelo kernel Kaggle. As versões exigidas são:

| Componente | Versão |
|---|---|
| Python do processamento | 3.11.17 |
| scikit-learn | 1.9.1 |
| NumPy | 2.4.6 |
| SciPy | 1.17.1 |

Se o runtime, o corpus ou o código divergir, o avaliador interrompe antes da busca. Os módulos realmente importados também são comparados com o snapshot, evitando verificar um checkout e executar outro. A saída não pode sobrescrever consultas, dados brutos ou arquivos congelados.

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
- A suíte completa passou com 63 testes, incluindo os dados reais do M1.
- As vinte consultas foram executadas em processo novo, com as versões e o snapshot conferidos antes e depois.
- O notebook foi executado em kernel local limpo, clonando o commit público fixado e provisionando o runtime isolado. As sete células de código terminaram sem erros e produziram um relatório idêntico byte a byte ao da primeira execução.
- A revisão independente não identificou achados acionáveis no avaliador ou no bootstrap do notebook.

**A execução e a publicação na plataforma Kaggle ainda dependem do autor.** O ensaio local verifica código, bootstrap e reprodução, mas não verifica a autenticação, as permissões de Internet, os anexos ou as condições do runtime hospedado. O M4 permanece aguardando essa confirmação; M5 e M6 não foram iniciados.

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
