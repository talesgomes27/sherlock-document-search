import base64
import hashlib
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
BUILD = runpy.run_path(str(ROOT / 'scripts/build_kaggle_bundle.py'))['build_bundle']


class KaggleBundleTests(unittest.TestCase):
    def test_embedded_bundle_matches_current_frozen_sources(self):
        notebook = json.loads((ROOT / 'notebooks/sherlock_document_search.ipynb').read_text())
        cell = next(cell for cell in notebook['cells'] if 'embedded-code' in cell['metadata'].get('tags', []))
        header = ''.join(cell['source']).split('# END EMBEDDED PAYLOAD', 1)[0]
        values = {}
        exec(header, {'__builtins__': {}}, values)
        payload = base64.b64decode(values['BUNDLE_B64'], validate=True)
        self.assertEqual(payload, BUILD(ROOT))
        self.assertEqual(hashlib.sha256(payload).hexdigest(), values['BUNDLE_SHA256'])
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            snapshot = json.loads((ROOT / 'evaluation/m3_freeze.json').read_text())
            expected = set(snapshot['file_sha256']) | {'evaluation/m3_freeze.json',
                         'src/sherlock_search/final_evaluation.py', 'README.md'}
            self.assertEqual(set(archive.namelist()), expected)
            for name in expected - {'README.md'}:
                self.assertEqual(archive.read(name), (ROOT / name).read_bytes())
            self.assertFalse(any(name.endswith('.txt') or name.startswith('data/') for name in archive.namelist()))

    def test_changed_frozen_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'evaluation').mkdir()
            (root / 'source.py').write_text('changed')
            (root / 'evaluation/m3_freeze.json').write_text(json.dumps({'file_sha256': {'source.py': 'expected'}}))
            with self.assertRaisesRegex(ValueError, 'Frozen input changed: source.py'):
                BUILD(root)


if __name__ == '__main__':
    unittest.main()
