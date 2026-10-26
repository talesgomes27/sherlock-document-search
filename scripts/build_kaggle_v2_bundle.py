"""Embed the frozen v2 experiment and reference report in its own Kaggle notebook."""

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile


PRIVATE_FINAL = 'data/processed/v2_holdout/final.json'


def read_inside(root, name):
    if (not isinstance(name, str) or not name or Path(name).is_absolute()
            or '\\' in name or '..' in Path(name).parts or Path(name).as_posix() != name):
        raise ValueError(f'Invalid bundle path: {name}')
    path = (root/name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Bundle path outside project: {name}')
    return path.read_bytes()


def build_bundle(root):
    frozen = read_inside(root, 'evaluation/v2/freeze.json')
    snapshot = json.loads(frozen)
    files = {}
    for name, expected in snapshot['file_sha256'].items():
        source = 'evaluation/v2/final.json' if name == PRIVATE_FINAL else name
        content = read_inside(root, source)
        if (not isinstance(expected, str) or re.fullmatch('[0-9a-f]{64}', expected) is None
                or hashlib.sha256(content).hexdigest() != expected):
            raise ValueError(f'Frozen input changed: {name}')
        files[name] = content
    reference = read_inside(root, 'reports/v2/final.json')
    evidence = json.loads(read_inside(root, 'reports/v2/validation.json'))
    if (hashlib.sha256(reference).hexdigest() != evidence['final_report_sha256']
            or json.loads(reference)['freeze_sha256'] != hashlib.sha256(frozen).hexdigest()):
        raise ValueError('Reference final report or freeze changed.')
    files['evaluation/v2/freeze.json'] = frozen
    files['reports/v2/final.json'] = reference
    files['README.md'] = b'# Sherlock Holmes search comparison\n\nFrozen analysis code and metadata for this notebook.\n'
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)
    return output.getvalue()


def refresh(root, check=False):
    path = root/'notebooks/sherlock_document_search_v2.ipynb'
    notebook = json.loads(path.read_text(encoding='utf-8'))
    cells = [cell for cell in notebook['cells'] if 'embedded-code-v2' in cell['metadata'].get('tags', [])]
    if len(cells) != 1:
        raise ValueError('Expected one embedded-code-v2 cell.')
    cell = cells[0]
    source = ''.join(cell['source'])
    payload = build_bundle(root)
    header = f'BUNDLE_B64 = "{base64.b64encode(payload).decode()}"\nBUNDLE_SHA256 = "{hashlib.sha256(payload).hexdigest()}"\n'
    source = header + '# END EMBEDDED PAYLOAD\n' + source.split('# END EMBEDDED PAYLOAD\n', 1)[1]
    if check:
        if source != ''.join(cell['source']):
            raise ValueError('Notebook code bundle is out of date.')
    else:
        cell['source'] = source
        for item in notebook['cells']:
            if item['cell_type'] == 'code':
                item['execution_count'], item['outputs'] = None, []
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1)+'\n', encoding='utf-8')
    print(f'V2 notebook bundle verified: {len(payload)} bytes; no source books included.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    refresh(Path(__file__).resolve().parents[1], check=args.check)
