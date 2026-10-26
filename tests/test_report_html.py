import copy
import json
from pathlib import Path
import runpy
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATE = runpy.run_path(str(ROOT / 'scripts/check_report.py'))['validate_site']


def table(identifier, rows):
    return f'<div id="{identifier}"><table>' + ''.join(
        '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
        for row in rows) + '</table></div>'


class ReportHTMLTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.output = self.root / 'output'
        self.output.mkdir()
        methods = {}
        for key, hits, false_positives, mrr in [('literal_v1', 2, 0, .1),
                                              ('tfidf_v1', 3, 6, .2), ('bm25', 4, 6, .3)]:
            methods[key] = {'positive_hits': hits, 'positive_queries': 5,
                            'false_positive_queries': false_positives,
                            'negative_queries': 6, 'mrr_at_5': mrr}
        self.v2 = {'methods': methods,
                   'corpus_totals': {'files': 2, 'paragraphs': 12,
                                     'retained_words': 1234, 'removed_words': 5},
                   'results': [{'id': f'v2-final-{number}', 'answerable': False,
                                'literal_v1': [], 'tfidf_v1': [{'score': .123456}],
                                'bm25': [{'score': 10.123456}]} for number in range(19, 25)]}
        self.v1 = {'literal': {'positive_hits': 1, 'positive_queries': 3,
                              'false_positive_queries': 0, 'negative_queries': 4},
                   'tfidf': {'positive_hits': 2, 'positive_queries': 3,
                            'false_positive_queries': 4, 'negative_queries': 4}}
        self.write_json('reports/m4_final.json', self.v1)
        self.write_json('reports/v2/final.json', self.v2)
        positives = 'Positivas com referência no top 5'
        negatives = 'Negativas com retorno'
        self.html = ''.join([
            '<link rel="stylesheet" href="styles/main.css?version=1">',
            '<script src="/sherlock-document-search/app.js"></script>',
            '<a href="nested/other.html?x=1#other%20anchor">Other page</a>',
            '<a href="https://example.invalid/not-checked">External</a>',
            '<a href="mailto:reader@example.invalid">Mail</a>',
            '<img src="data:image/png;base64,AAAA" alt="Decorative example">',
            '<div id="fig-corpus"><img src="plot%20one.png" alt="Corpus counts"',
            ' srcset="plot%20one.png 1x, second.png 2x"></div>',
            '<div id="fig-comparison"><img src="second.png" alt="Comparison"></div>',
            *[f'<a href="#{identifier}">{identifier}</a>' for identifier in
              ['fig-corpus', 'fig-comparison', 'tbl-corpus', 'tbl-results',
               'tbl-negatives', 'tbl-history']],
            table('tbl-corpus', [['Medida', 'Quantidade'], ['Arquivos TXT', '2'],
                                ['Parágrafos retidos', '12'], ['Palavras retidas', '1.234'],
                                ['Palavras excluídas pelos recortes', '5']]),
            table('tbl-results', [['Método', positives, negatives, 'MRR@5 nas positivas'],
                                 ['Literal', '2/5', '0/6', '0,1000'],
                                 ['TF-IDF', '3/5', '6/6', '0,2000'],
                                 ['BM25', '4/5', '6/6', '0,3000']]),
            table('tbl-history', [['Método', positives, negatives], ['Literal', '1/3', '0/4'],
                                 ['TF-IDF', '2/3', '4/4']]),
            table('tbl-negatives', [['ID', 'Detalhe solicitado', 'TF-IDF top 1',
                                    'BM25 top 1', 'Retornos literais'],
                                   *[[f'v2-final-{number}', 'Absent detail', '0,1235', '10,1235', '0']
                                     for number in range(19, 25)]])])
        self.write('index.html', self.html)
        self.write('nested/other.html', '<a id="other anchor" href="../index.html#tbl-results">Back</a>')
        self.write('styles/main.css', '@import "nested.css";body{background:url("../plot%20one.png?v=2")}')
        self.write('styles/nested.css', '@font-face{src:url("../font.woff2")}')
        for name in ['app.js', 'plot one.png', 'second.png', 'font.woff2']:
            self.write(name, '')

    def write(self, name, content):
        path = self.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    def write_json(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding='utf-8')

    def test_complete_site_links_css_anchors_and_public_inputs(self):
        frozen = copy.deepcopy((self.v1, self.v2))
        stats = VALIDATE(self.output, self.root)
        self.assertEqual(stats['html_files'], 2)
        self.assertEqual(stats['css_files'], 2)
        self.assertEqual(stats['tables_checked'], 4)
        self.assertEqual(stats['images'], 3)
        self.assertGreater(stats['checked_local_links'], 15)
        self.assertEqual((self.v1, self.v2), frozen)
        self.assertFalse((self.root / 'data').exists())

    def test_broken_links_in_html_srcset_css_and_target_anchors(self):
        changes = [('index.html', self.html.replace('second.png 2x', 'missing.png 2x'), 'Missing local'),
                   ('styles/nested.css', '@font-face{src:url("missing.woff2")}', 'Missing local'),
                   ('nested/other.html', '<a id="other anchor" href="../index.html#absent">Bad</a>', 'Missing HTML anchor'),
                   ('nested/other.html', '<a id="other anchor" href="../../outside.png">Escape</a>', 'escapes output'),
                   ('nested/other.html', '<a id="other anchor" href="file:///tmp/private.png">File</a>', 'File URL')]
        for name, value, message in changes:
            with self.subTest(name=name, message=message):
                path = self.output / name
                before = path.read_text()
                self.write(name, value)
                with self.assertRaisesRegex(ValueError, message):
                    VALIDATE(self.output, self.root)
                self.write(name, before)

    def test_final_history_and_negative_tables_use_separate_json_values(self):
        for old, new, identifier in [('2/5', '2/3', 'tbl-results'),
                                     ('1/3', '2/5', 'tbl-history'),
                                     ('10,1235', '10,1234', 'tbl-negatives'),
                                     ('v2-final-24', 'v2-final-99', 'tbl-negatives'),
                                     ('1.234', '1.235', 'tbl-corpus')]:
            with self.subTest(identifier=identifier, value=new):
                self.write('index.html', self.html.replace(f'<td>{old}</td>', f'<td>{new}</td>'))
                with self.assertRaisesRegex(ValueError, identifier):
                    VALIDATE(self.output, self.root)
        self.write('index.html', self.html)
        self.v2['methods']['bm25']['positive_hits'] = 5
        self.write_json('reports/v2/final.json', self.v2)
        with self.assertRaisesRegex(ValueError, 'tbl-results'):
            VALIDATE(self.output, self.root)

    def test_missing_accessibility_figures_and_crossrefs_are_rejected(self):
        for html, message in [(self.html.replace('alt="Corpus counts"', ''), 'alt text'),
                              (self.html.replace('id="fig-corpus"', 'id="changed"'), 'Missing HTML anchor'),
                              (self.html.replace('href="#tbl-history"', 'href="#tbl-results"'), 'cross-reference'),
                              (self.html + '<p>Figure ??</p>', 'Unresolved cross-reference')]:
            with self.subTest(message=message):
                self.write('index.html', html)
                with self.assertRaisesRegex(ValueError, message):
                    VALIDATE(self.output, self.root)

    def test_published_corpus_notebooks_and_source_code_are_rejected(self):
        for name in ['books/original.txt', 'notebook.ipynb', 'index.qmd', 'helper.py', 'data/raw/corpus.json']:
            with self.subTest(name=name):
                self.write(name, 'source')
                with self.assertRaisesRegex(ValueError, 'Forbidden source/corpus'):
                    VALIDATE(self.output, self.root)
                (self.output / name).unlink()
        self.write('robots.txt', 'User-agent: *')
        self.assertEqual(VALIDATE(self.output, self.root)['tables_checked'], 4)


if __name__ == '__main__':
    unittest.main()
