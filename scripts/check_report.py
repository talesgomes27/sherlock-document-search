"""Check the rendered report, local resources and published JSON-backed tables."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PROJECT_PATH = '/sherlock-document-search/'
REQUIRED_IDS = {'fig-corpus', 'fig-comparison', 'fig-positions', 'tbl-corpus', 'tbl-results',
                'tbl-negatives', 'tbl-history'}
VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
             'link', 'meta', 'param', 'source', 'track', 'wbr'}
CSS_URL = re.compile(r'''url\(\s*['"]?([^'"\)]+)['"]?\s*\)|@import\s+['"]([^'"]+)['"]''', re.I)


def normalized(value):
    return ' '.join(value.split())


class ReportHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.images = []
        self.tables = []
        self.stack = []
        self.table = None
        self.row = None
        self.cell = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag == 'a' and attrs.get('name'):
            self.ids.add(attrs['name'])
        for attribute in ('href', 'src'):
            if attribute in attrs:
                self.links.append(attrs[attribute])
        if 'srcset' in attrs:
            # shortcut: ordinary image candidates, extend for escaped URL whitespace if introduced.
            self.links.extend(re.findall(r'(?:^|,)\s*(data:[^\s]+|[^\s,]+)(?:\s+[^,]+)?', attrs['srcset']))
        if 'style' in attrs:
            self.links.extend(first or second for first, second in CSS_URL.findall(attrs['style']))
        ancestors = {identifier for _, identifier in self.stack if identifier}
        if tag == 'img':
            self.images.append((attrs, ancestors | {attrs.get('id')}))
        if tag == 'table':
            self.table = {'ids': ancestors | {attrs.get('id')}, 'rows': []}
        elif tag == 'tr' and self.table is not None:
            self.row = []
        elif tag in {'th', 'td'} and self.row is not None:
            self.cell = []
        if tag not in VOID_TAGS:
            self.stack.append((tag, attrs.get('id')))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in {'th', 'td'} and self.cell is not None:
            self.row.append(normalized(''.join(self.cell)))
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            self.table['rows'].append(self.row)
            self.row = None
        elif tag == 'table' and self.table is not None:
            self.tables.append(self.table)
            self.table = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)
        if any(tag == 'style' for tag, _ in self.stack):
            self.links.extend(first or second for first, second in CSS_URL.findall(data))
        if not any(tag in {'script', 'style'} for tag, _ in self.stack):
            self.text.append(data)


def local_target(url, source, output):
    parsed = urlsplit(url)
    if parsed.scheme == 'file':
        raise ValueError(f'File URL outside published project: {source}: {url}')
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if path.startswith(PROJECT_PATH):
        target = output / path[len(PROJECT_PATH):]
    elif path == PROJECT_PATH.rstrip('/'):
        target = output / 'index.html'
    elif path.startswith('/'):
        raise ValueError(f'Local URL outside project base: {source}: {url}')
    elif path:
        target = source.parent / path
    else:
        target = source
    target = target.resolve()
    if not target.is_relative_to(output):
        raise ValueError(f'Local URL escapes output: {source}: {url}')
    if target.is_dir():
        target /= 'index.html'
    if not target.is_file():
        raise ValueError(f'Missing local resource: {source}: {url}')
    return target, unquote(parsed.fragment)


def expected_tables(root):
    v1 = json.loads((root / 'reports/m4_final.json').read_text())
    v2 = json.loads((root / 'reports/v2/final.json').read_text())
    counts = v2['corpus_totals']
    fmt = lambda value: f'{value:.4f}'.replace('.', ',')
    pair = lambda value, first, total: f'{value[first]}/{value[total]}'
    positives = 'Positivas com referência no top 5'
    negatives = 'Negativas com retorno'
    tables = {
        'tbl-corpus': [
            ['Medida', 'Quantidade'],
            *[[label, f'{counts[key]:,}'.replace(',', '.')]
              for label, key in [('Arquivos TXT', 'files'), ('Parágrafos retidos', 'paragraphs'),
                                 ('Palavras retidas', 'retained_words'),
                                 ('Palavras excluídas pelos recortes', 'removed_words')]]],
        'tbl-results': [['Método', positives, negatives, 'MRR@5 nas positivas']],
        'tbl-history': [['Método', positives, negatives]],
        'tbl-negatives': [['ID', 'Detalhe solicitado', 'TF-IDF top 1', 'BM25 top 1', 'Retornos literais']],
    }
    for key, name in [('literal_v1', 'Literal'), ('tfidf_v1', 'TF-IDF'), ('bm25', 'BM25')]:
        result = v2['methods'][key]
        tables['tbl-results'].append([name, pair(result, 'positive_hits', 'positive_queries'),
                                     pair(result, 'false_positive_queries', 'negative_queries'),
                                     fmt(result['mrr_at_5'])])
    for key, name in [('literal', 'Literal'), ('tfidf', 'TF-IDF')]:
        result = v1[key]
        tables['tbl-history'].append([name, pair(result, 'positive_hits', 'positive_queries'),
                                     pair(result, 'false_positive_queries', 'negative_queries')])
    for result in v2['results']:
        if not result['answerable']:
            tables['tbl-negatives'].append([result['id'], None,
                                            fmt(result['tfidf_v1'][0]['score']),
                                            fmt(result['bm25'][0]['score']),
                                            str(len(result['literal_v1']))])
    return tables


def validate_site(output, root=ROOT):
    output, root = Path(output).resolve(), Path(root).resolve()
    files = [path for path in output.rglob('*') if path.is_file()]
    for path in files:
        relative = path.relative_to(output)
        if not path.resolve().is_relative_to(output):
            raise ValueError(f'Artifact symlink escapes output: {relative}')
        if (path.suffix.lower() in {'.ipynb', '.qmd', '.py'}
                or (path.suffix.lower() == '.txt' and relative.as_posix() != 'robots.txt')
                or relative.parts[:2] == ('data', 'raw')):
            raise ValueError(f'Forbidden source/corpus in artifact: {relative}')
    pages = {}
    for path in files:
        if path.suffix.lower() == '.html':
            page = ReportHTML()
            page.feed(path.read_text(encoding='utf-8'))
            page.close()
            pages[path] = page
    index = output / 'index.html'
    if index not in pages:
        raise ValueError('Missing report index.html')
    checked = 0
    css_seen = set()

    def check_link(url, source):
        nonlocal checked
        result = local_target(url, source, output)
        if result is None:
            return
        checked += 1
        target, fragment = result
        if fragment and target in pages and fragment not in pages[target].ids:
            raise ValueError(f'Missing HTML anchor: {source}: {url}')
        if target.suffix.lower() == '.css' and target not in css_seen:
            css_seen.add(target)
            css = re.sub(r'/\*.*?\*/', '', target.read_text(encoding='utf-8'), flags=re.S)
            for first, second in CSS_URL.findall(css):
                check_link((first or second).strip(), target)

    for path, page in pages.items():
        if '??' in ''.join(page.text) or any('unresolved' in url for url in page.links):
            raise ValueError(f'Unresolved cross-reference in {path}')
        for url in page.links:
            check_link(url, path)
        for attrs, _ in page.images:
            if not normalized(attrs.get('alt', '')):
                raise ValueError(f'Image missing nonempty alt text: {path}: {attrs.get("src")}')
    page = pages[index]
    missing = REQUIRED_IDS - page.ids
    if missing:
        raise ValueError(f'Missing report figures/tables: {sorted(missing)}')
    linked = set()
    for url in page.links:
        result = local_target(url, index, output)
        if result and result[0] == index:
            linked.add(result[1])
    if REQUIRED_IDS - linked:
        raise ValueError(f'Missing report cross-reference links: {sorted(REQUIRED_IDS - linked)}')
    for identifier in ('fig-corpus', 'fig-comparison', 'fig-positions'):
        if not any(identifier in ancestors and attrs.get('src') for attrs, ancestors in page.images):
            raise ValueError(f'Missing image in figure {identifier}')
    for identifier, expected in expected_tables(root).items():
        candidates = [table for table in page.tables if identifier in table['ids']]
        if len(candidates) != 1:
            raise ValueError(f'Missing or ambiguous table {identifier}')
        rows = candidates[0]['rows']
        if not rows:
            raise ValueError(f'Table {identifier} is empty')
        if identifier == 'tbl-results' and not any('MRR@5' in cell for cell in rows[0]):
            raise ValueError('tbl-results missing MRR@5 header')
        if len(rows) != len(expected):
            raise ValueError(f'Table {identifier} has wrong number of rows')
        for actual, wanted in zip(rows, expected):
            if len(actual) != len(wanted) or any(
                    actual_cell != expected_cell if expected_cell is not None else not actual_cell
                    for actual_cell, expected_cell in zip(actual, wanted)):
                raise ValueError(f'Table {identifier} differs from public JSON: {actual!r}; expected {wanted!r}')
    return {'html_files': len(pages), 'checked_local_links': checked,
            'css_files': len(css_seen), 'tables_checked': 4,
            'images': sum(len(page.images) for page in pages.values()),
            'crossrefs_checked': len(REQUIRED_IDS)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'site/_site')
    args = parser.parse_args()
    try:
        print(json.dumps(validate_site(args.output), separators=(',', ':')))
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'Report check failed: {error}\n')


if __name__ == '__main__':
    main()
