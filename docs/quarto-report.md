# M5 — relatório Quarto e GitHub Pages

O autor autorizou o merge do PR #1 e o início do M5 em 25 de outubro de 2026. O PR foi integrado por merge commit `95fda2e`, com dois pais, preservando a sequência v1/v2. Este marco publica um relatório HTML com fontes em `site/`, separado dos notebooks e dos arquivos congelados.

## Conteúdo e origem

O relatório apresenta corpus, preparação, três métodos, protocolo, comparação v2, seis negativas, reprodução e um histórico v1 separado. Tabelas são construídas a partir dos JSONs aprovados e figuras reutilizam os PNGs da v2; não há novo ajuste, busca ou avaliação de modelos. O texto publica metadados e paráfrases, sem trechos dos livros. A pendência sobre condições de exibição de trechos continua documentada em `docs/provenance.md`.

`scripts/verify_report_sources.py` confere os 48 arquivos do snapshot v2 e os hashes do relatório final e do próprio snapshot. O caminho de metadados finais antes reservado usa a cópia pública byte-idêntica. Assim, o render não precisa dos TXT nem dos arquivos privados de revisão. O ambiente não instala scikit-learn: só executa leitura de JSON e formatação das tabelas.

## Renderização local

Requisitos: Quarto **1.10.19**, Python **3.11.17** e ambiente separado. As dependências dos modelos em pyproject/uv.lock permanecem intactas.

```bash
uv venv --python 3.11.17 .venv-report
uv pip install --python .venv-report/bin/python -r site/requirements.txt
.venv-report/bin/python scripts/render_report.py
.venv-report/bin/python scripts/check_report.py
```

O renderizador registra o kernel `sherlock-report` apenas no prefixo desse ambiente e informa explicitamente o Python ao Quarto. As cinco células são executadas sobre resultados existentes, com cache/freeze do Quarto desabilitados; o congelamento científico é validado por hashes. PyYAML é uma dependência do engine Jupyter do Quarto, separada das dependências dos modelos.

O HTML sai em `site/_site/`, ignorado pelo Git. A metadata `_build.json` identifica commit, estado da árvore, versão do Quarto/Python, hashes das fontes e dos arquivos produzidos. Prévias de uma árvore com mudanças locais não são confundidas com publicação de um commit limpo.

## Publicação por GitHub Actions

Destino: [relatório no GitHub Pages](https://talesgomes27.github.io/sherlock-document-search/). O workflow `.github/workflows/report-pages.yml` constrói e verifica o relatório e publica apenas o artifact daquele build. Não usa branch `gh-pages` nem `/docs` como diretório de HTML.

A configuração inicial do repositório precisa usar Pages com `build_type: workflow`. PRs executam somente build e verificações, com `contents: read` e sem credenciais persistidas. Upload e deploy ficam restritos à `main`, com `pages: write` e `id-token: write` apenas no job de deploy. Alterações apenas em README, registro, documentação ou evidências do M5 não geram outro deploy; alterações no relatório ou nas fontes verificadas o fazem.

O fluxo fixa Quarto 1.10.19 e Python 3.11.17, instala ferramentas de `site/requirements.txt`, executa os testes de fontes, HTML, posições e preservação das cópias dos notebooks, renderiza, verifica o resultado e só então envia `site/_site`. A execução remota de testes do relatório não é apresentada como execução da suíte de modelos com o corpus real.

## Verificações e recuperação

O checker percorre HTML, links e recursos locais, CSS, âncoras, referências cruzadas, textos alternativos e quatro tabelas contra os JSONs originais. Recusa publicação de arquivos-fonte/corpus dentro do artifact. A inspeção visual complementar confere leitura, navegação e figuras no navegador.

Depois do deploy, confira a conclusão do run, URL final e `_build.json`: o commit publicado e o hash do relatório v2 devem coincidir com o artifact validado. Confira também HTML e assets críticos contra os hashes do build remoto. Comando submetido ou URL emitida não bastam para declarar publicação concluída.

Se uma alteração futura falhar no build, o deploy não avança e o site anterior permanece. Para recuperar uma versão publicada, restaure as fontes do último commit aprovado por um commit de reversão revisável e execute novamente o fluxo, sem reescrever histórico ou manifests científicos. Mudança de resultados exige outro protocolo; não se edita o snapshot para corrigir aparência.

Fontes operacionais: [Quarto/Python](https://quarto.org/docs/computations/python.html), [Quarto/Pages](https://quarto.org/docs/publishing/github-pages.html) e [workflow de Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).


## Publicação verificada do M5

O [run 40256849352](https://github.com/talesgomes27/sherlock-document-search/actions/runs/40256849352) concluiu build e deploy do commit `b55ff7027641d3e4421cc95ca919f9c6626070a1`. A página pública respondeu HTTP 200; os 21 arquivos publicados conferiram com os hashes do build, assim como os 50 hashes de entrada. As quatro tabelas foram verificadas contra os JSONs aprovados e a apresentação foi inspecionada no navegador.

A evidência está em [publication_validation.json](../reports/m5/publication_validation.json) e na [captura da publicação](../reports/m5/publication.png). A suíte local passou com 115 testes, sem ignorados; o workflow remoto passou nos nove testes específicos do relatório. Ambos os notebooks e os arquivos congelados permanecem intactos. O commit que acrescenta esta evidência altera apenas documentação e não dispara novo deploy.


A [revisão editorial](editorial-presentation.md) simplifica a leitura e acrescenta uma terceira figura, com a posição das referências por consulta. As cinco células de código do relatório e todos os resultados científicos continuam iguais. A evidência inicial do M5 acima descreve a publicação anterior; a revisão é entregue separadamente para aprovação.


A revisão editorial foi posteriormente aprovada no PR #2 e publicada a partir do merge commit `235fc36`. O [run 40258089685](https://github.com/talesgomes27/sherlock-document-search/actions/runs/40258089685) concluiu build e deploy; a [verificação no destino](../reports/m5/pr2_publication_validation.json) confirma a página com três gráficos e quatro tabelas. Os registros anteriores preservam a cronologia da prévia e da publicação inicial do M5.
