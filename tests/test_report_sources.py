import hashlib
import json
from pathlib import Path
import runpy
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VERIFY = runpy.run_path(str(ROOT/'scripts/verify_report_sources.py'))['verify_report_sources']


def digest(value):
    return hashlib.sha256(value).hexdigest()


class ReportSourcesTests(unittest.TestCase):
    def fixture(self, root):
        values = {'reports/m4_final.json': {'split': 'final'},
                  'reports/m1_quality.json': {'totals': {'files': 9}},
                  'evaluation/v2/final.json': [],
                  'evaluation/v2/configuration_decision.json': {'bm25': {'min_score': 0}}}
        frozen = {}
        for name, value in values.items():
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(value))
            key='data/processed/v2_holdout/final.json' if name=='evaluation/v2/final.json' else name
            frozen[key]=digest(path.read_bytes())
        self.write_snapshot(root, frozen)

    def write_snapshot(self, root, frozen):
        path=root/'evaluation/v2/freeze.json'
        path.write_text(json.dumps({'file_sha256': frozen}))
        report=json.dumps({'split':'v2_final','freeze_sha256':digest(path.read_bytes()),'methods':{}}).encode()
        (root/'reports/v2').mkdir(parents=True,exist_ok=True)
        (root/'reports/v2/final.json').write_bytes(report)
        (root/'reports/v2/validation.json').write_text(json.dumps({'final_report_sha256':digest(report)}))

    def test_real_public_sources_without_loading_models(self):
        result=VERIFY(ROOT)
        self.assertEqual(result['v2']['methods']['bm25']['positive_hits'],12)
        self.assertEqual(result['v1']['literal']['positive_hits'],7)
        self.assertEqual(result['corpus']['totals']['files'],9)
        self.assertEqual(len(result['source_hashes']),50)

    def test_no_private_holdout_or_raw_corpus_is_needed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root)
            result=VERIFY(root)
            self.assertEqual(result['queries_v2'],[])
            self.assertFalse((root/'data').exists())

    def test_changed_inputs_and_final_report_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root)
            path=root/'reports/m1_quality.json';before=path.read_bytes();path.write_text('{}')
            with self.assertRaisesRegex(ValueError,'congelad'):
                VERIFY(root)
            path.write_bytes(before)
            (root/'reports/v2/final.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'final'):
                VERIFY(root)

    def test_manifest_cannot_read_outside_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root)
            frozen=json.loads((root/'evaluation/v2/freeze.json').read_text())['file_sha256']
            frozen['../private.txt']='a'*64
            self.write_snapshot(root,frozen)
            with self.assertRaisesRegex(ValueError,'Caminho'):
                VERIFY(root)


if __name__=='__main__':unittest.main()
