import ast
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
BUILD = runpy.run_path(str(ROOT / 'scripts/build_kaggle_v2_bundle.py'))
PRIVATE_FINAL = 'data/processed/v2_holdout/final.json'


class KaggleV2BundleTests(unittest.TestCase):
    def test_bundle_matches_snapshot_and_uses_published_final_metadata(self):
        payload = BUILD['build_bundle'](ROOT)
        self.assertEqual(payload, BUILD['build_bundle'](ROOT))
        notebook = json.loads((ROOT/'notebooks/sherlock_document_search_v2.ipynb').read_text())
        cell = next(cell for cell in notebook['cells'] if 'embedded-code-v2' in cell['metadata'].get('tags', []))
        header = ''.join(cell['source']).split('# END EMBEDDED PAYLOAD', 1)[0]
        values = {node.targets[0].id: ast.literal_eval(node.value) for node in ast.parse(header).body}
        self.assertEqual(base64.b64decode(values['BUNDLE_B64'], validate=True), payload)
        self.assertEqual(values['BUNDLE_SHA256'], hashlib.sha256(payload).hexdigest())
        snapshot = json.loads((ROOT / 'evaluation/v2/freeze.json').read_text())
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            self.assertEqual(set(archive.namelist()), set(snapshot['file_sha256']) |
                             {'evaluation/v2/freeze.json', 'README.md', 'reports/v2/final.json'})
            for name, expected in snapshot['file_sha256'].items():
                self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), expected)
            self.assertEqual(archive.read(PRIVATE_FINAL), (ROOT / 'evaluation/v2/final.json').read_bytes())
            self.assertFalse(any(name.startswith('data/raw/') or name.endswith('/review.md') for name in archive.namelist()))
            self.assertEqual([name for name in archive.namelist() if name.startswith('data/')], [PRIVATE_FINAL])

    def fixture(self, root):
        for name, content in [('src/frozen.py', b'frozen'), ('evaluation/v2/final.json', b'[]')]:
            path = root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
        snapshot = {'file_sha256': {'src/frozen.py': hashlib.sha256(b'frozen').hexdigest(),
                                   PRIVATE_FINAL: hashlib.sha256(b'[]').hexdigest()}}
        path = root/'evaluation/v2/freeze.json';path.write_text(json.dumps(snapshot))
        report = json.dumps({'freeze_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}).encode()
        (root/'reports/v2').mkdir(parents=True,exist_ok=True)
        (root/'reports/v2/final.json').write_bytes(report)
        (root/'reports/v2/validation.json').write_text(json.dumps({'final_report_sha256': hashlib.sha256(report).hexdigest()}))

    def test_builder_works_without_local_holdout_and_refuses_changed_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);self.fixture(root)
            self.assertFalse((root/PRIVATE_FINAL).exists())
            with zipfile.ZipFile(io.BytesIO(BUILD['build_bundle'](root))) as archive:
                self.assertEqual(archive.read(PRIVATE_FINAL), b'[]')
            (root/'src/frozen.py').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'Frozen input changed'):
                BUILD['build_bundle'](root)

    def test_builder_refuses_changed_reference_and_paths_outside_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);self.fixture(root)
            (root/'reports/v2/final.json').write_text('{}')
            with self.assertRaises(ValueError):
                BUILD['build_bundle'](root)
            self.fixture(root)
            path = root/'evaluation/v2/freeze.json';snapshot=json.loads(path.read_text())
            snapshot['file_sha256']['../outside.py'] = 'a'*64
            path.write_text(json.dumps(snapshot))
            with self.assertRaises(ValueError):
                BUILD['build_bundle'](root)

    def test_refresh_updates_only_v2_and_check_detects_stale_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root);(root/'notebooks').mkdir()
            v1=root/'notebooks/sherlock_document_search.ipynb';v1.write_bytes(b'v1 sentinel')
            path=root/'notebooks/sherlock_document_search_v2.ipynb'
            notebook={'cells':[{'cell_type':'code','metadata':{'tags':['embedded-code-v2']},
                               'source':'BUNDLE_B64 = ""\nBUNDLE_SHA256 = ""\n# END EMBEDDED PAYLOAD\nprint("ready")\n',
                               'outputs':[{'text':'old'}],'execution_count':1}]}
            path.write_text(json.dumps(notebook))
            with self.assertRaisesRegex(ValueError,'out of date'):
                BUILD['refresh'](root,check=True)
            BUILD['refresh'](root);BUILD['refresh'](root,check=True)
            self.assertEqual(v1.read_bytes(),b'v1 sentinel')
            cell=json.loads(path.read_text())['cells'][0]
            self.assertEqual(cell['outputs'],[]);self.assertIsNone(cell['execution_count'])
            for node in ast.parse(cell['source'].split('# END EMBEDDED PAYLOAD')[0]).body:
                self.assertIsInstance(ast.literal_eval(node.value),str)


if __name__ == '__main__':
    unittest.main()
