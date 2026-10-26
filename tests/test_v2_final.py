import copy
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import sherlock_search
from sherlock_search.final_evaluation import runtime_versions
from sherlock_search.tfidf import TfidfSearch
from sherlock_search.v2_final import (
    REQUIRED_FROZEN_PATHS, evaluate_final, load_final, main, metrics,
    validate_final_output, verify_freeze_v2,
)


BM25 = {'k1': 1.2, 'b': 0.75, 'min_score': 0.0}
TYPES = {'exact': 6, 'paraphrase': 6, 'context': 6, 'unanswerable': 6}
FINAL_PATH = 'data/processed/v2_holdout/final.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')


class FinalV2Tests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        package = Path(sherlock_search.__file__).resolve().parent
        for name in ('v2_final.py', 'bm25.py', 'v2_development.py', 'development.py',
                     'final_evaluation.py', 'corpus.py', 'search.py', 'tfidf.py',
                     'tfidf_config.json', 'corpus_manifest.json'):
            destination = self.root / 'src/sherlock_search' / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((package / name).read_bytes())
        self.queries = []
        for number in range(1, 25):
            positive = number <= 18
            query = {'id': f'v2-final-{number:02}', 'query': 'ruby emerald' if positive else 'phantom',
                     'answerable': positive, 'relevant_ids': ['synthetic:1'] if positive else [],
                     'query_type': ('exact', 'paraphrase', 'context')[(number - 1) // 6] if positive else 'unanswerable',
                     'review_status': 'approved', 'rationale': 'Synthetic known reference or checked absence.'}
            if not positive:
                query['negative_verification'] = {
                    'method': 'synthetic inspection', 'kind': 'unreported detail',
                    'finding': 'Synthetic detail absent.', 'scope': 'synthetic corpus',
                    'uncertainty': 'Known-reference fixture only.', 'evidence_ids': ['synthetic:2']}
            self.queries.append(query)
        self.protocol = {'schema_version': 1, 'final': {'queries': 24, 'answerable': 18,
                         'unanswerable': 6, 'query_types': TYPES}, 'bm25': {'k1': 1.2, 'b': 0.75},
                         'thresholds': [0, 0.5, 1, 2, 4, 8, 16, 32],
                         'selection_rule': 'maximize_balanced_utility_then_minimize_false_positive_rate_then_minimize_threshold',
                         'final_queries_executed': False}
        write_json(self.root / 'evaluation/v2/protocol.json', self.protocol)
        write_json(self.root / 'evaluation/v2/configuration_decision.json', {'bm25': BM25})
        write_json(self.root / 'evaluation/v2/development.json', {'synthetic': True})
        write_json(self.root / 'reports/v2/development.approved.json', {'synthetic': True})
        self._write_queries(self.queries)
        preserved = {}
        for number in range(35):
            path = self.root / f'synthetic/v1-{number:02}.txt'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'preserved synthetic asset {number}', encoding='utf-8')
            preserved[str(path.relative_to(self.root))] = digest(path)
        write_json(self.root / 'evaluation/v2/v1_preservation.json', {'file_sha256': preserved})
        self.v1_snapshot = {'file_sha256': dict(list(preserved.items())[:15]),
                            'runtime_versions': runtime_versions(),
                            'tfidf': {'min_score': TfidfSearch([]).min_score, 'vectorizer': 'frozen defaults'}}
        write_json(self.root / 'evaluation/m3_freeze.json', self.v1_snapshot)
        self.snapshot = {'scope': 'v2_final', 'bm25': BM25, 'runtime_versions': runtime_versions(),
                         'final_queries_executed': False,
                         'file_sha256': {name: digest(self.root / name) for name in REQUIRED_FROZEN_PATHS}}
        self.snapshot['file_sha256'].update(preserved)
        self._write_freeze()
        self.raw_dir = self.root / 'data/raw'
        self.raw_dir.mkdir(parents=True)
        (self.raw_dir / 'synthetic.txt').write_text('synthetic corpus', encoding='utf-8')
        self.paragraphs = [
            {'id': 'synthetic:1', 'filename': 'synthetic.txt', 'title': 'Synthetic',
             'line_start': 1, 'line_end': 1, 'text': 'ruby emerald'},
            {'id': 'synthetic:2', 'filename': 'synthetic.txt', 'title': 'Synthetic',
             'line_start': 2, 'line_end': 2, 'text': 'sapphire'},
        ]
        self.corpus = {'totals': {'files': 1, 'paragraphs': 2},
                       'files': [{'filename': 'synthetic.txt', 'sha256': digest(self.raw_dir / 'synthetic.txt')}]}

    def _write_freeze(self, snapshot=None):
        write_json(self.root / 'evaluation/v2/freeze.json', self.snapshot if snapshot is None else snapshot)

    def _write_queries(self, queries):
        write_json(self.root / FINAL_PATH, queries)
        write_json(self.root / 'evaluation/v2/holdout_manifest.json', {
            'split': 'v2_final', 'status': 'approved_not_evaluated', 'query_count': 24,
            'positive': 18, 'negative': 6, 'type_counts': TYPES,
            'json_path': FINAL_PATH, 'json_sha256': digest(self.root / FINAL_PATH),
            'final_queries_executed': False})

    def _refresh_hash(self, name):
        self.snapshot['file_sha256'][name] = digest(self.root / name)
        self._write_freeze()

    def test_valid_freeze_and_approved_fixed_split(self):
        self.assertEqual(verify_freeze_v2(self.root), self.snapshot)
        self.assertEqual(load_final(self.root), self.queries)

    def test_invalid_freeze_fails_before_corpus_or_search(self):
        cases = []
        for key in ('scope', 'file_sha256', 'runtime_versions', 'bm25', 'final_queries_executed'):
            changed = copy.deepcopy(self.snapshot)
            del changed[key]
            cases.append(changed)
        for name, value in [('bm25', {**BM25, 'min_score': 32}),
                            ('bm25', {**BM25, 'min_score': False}),
                            ('final_queries_executed', 0),
                            ('runtime_versions', {**runtime_versions(), 'python': '3.11.18'})]:
            changed = copy.deepcopy(self.snapshot)
            changed[name] = value
            cases.append(changed)
        for relative, expected in [('../outside.txt', 'a' * 64),
                                   ('/absolute.txt', 'a' * 64), ('synthetic/bad.txt', 123),
                                   ('synthetic/bad.txt', 'not a digest')]:
            changed = copy.deepcopy(self.snapshot)
            changed['file_sha256'][relative] = expected
            cases.append(changed)
        missing = copy.deepcopy(self.snapshot)
        del missing['file_sha256']['src/sherlock_search/v2_final.py']
        cases.extend([missing, [], {'file_sha256': {}}])
        for changed in cases:
            with self.subTest(snapshot=changed):
                self._write_freeze(changed)
                with patch('sherlock_search.v2_final.prepare_corpus') as prepare:
                    with patch('sherlock_search.v2_final.load_final') as load:
                        with self.assertRaises((ValueError, OSError)):
                            evaluate_final(self.root, self.raw_dir)
                    load.assert_not_called()
                prepare.assert_not_called()

    def test_hash_tampering_and_imported_source_mismatch_are_rejected(self):
        report = self.root / 'reports/v2/development.approved.json'
        report.write_text('changed', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'congelado'):
            verify_freeze_v2(self.root)
        self._refresh_hash('reports/v2/development.approved.json')
        source = self.root / 'src/sherlock_search/v2_final.py'
        source.write_bytes(source.read_bytes() + b'\n')
        self._refresh_hash('src/sherlock_search/v2_final.py')
        with self.assertRaisesRegex(ValueError, 'importado'):
            verify_freeze_v2(self.root)

    def test_protocol_and_configuration_decision_cannot_change_fixed_parameters(self):
        changed = copy.deepcopy(self.protocol)
        changed['final']['queries'] = True
        write_json(self.root / 'evaluation/v2/protocol.json', changed)
        self._refresh_hash('evaluation/v2/protocol.json')
        with self.assertRaises(ValueError):
            verify_freeze_v2(self.root)
        write_json(self.root / 'evaluation/v2/protocol.json', self.protocol)
        self._refresh_hash('evaluation/v2/protocol.json')
        write_json(self.root / 'evaluation/v2/configuration_decision.json', {'bm25': {**BM25, 'min_score': 32}})
        self._refresh_hash('evaluation/v2/configuration_decision.json')
        with self.assertRaises(ValueError):
            verify_freeze_v2(self.root)

    def test_final_labels_reject_wrong_types_counts_and_incomplete_evidence(self):
        cases = [[], {}, self.queries[:-1]]
        for index, key, value in [(0, 'answerable', 1), (0, 'review_status', 'proposed'),
                                  (0, 'relevant_ids', []), (0, 'relevant_ids', ['synthetic:1', 'synthetic:1']),
                                  (0, 'query_type', 'unanswerable'), (0, 'query_type', []), (0, 'query', ' '),
                                  (0, 'rationale', None), (18, 'negative_verification', {}),
                                  (18, 'relevant_ids', ['synthetic:1']), (0, 'id', 'v2-dev-01')]:
            changed = copy.deepcopy(self.queries)
            changed[index][key] = value
            cases.append(changed)
        for changed in cases:
            with self.subTest(queries=changed):
                self._write_queries(changed)
                with self.assertRaises(ValueError):
                    load_final(self.root)
        self._write_queries(self.queries)
        manifest_path = self.root / 'evaluation/v2/holdout_manifest.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['positive'] = True
        write_json(manifest_path, manifest)
        with self.assertRaises(ValueError):
            load_final(self.root)

    def test_known_metrics_and_deterministic_methods_without_selection(self):
        with patch('sherlock_search.v2_final.prepare_corpus', return_value=(self.paragraphs, self.corpus)):
            before = copy.deepcopy(self.snapshot)
            report = evaluate_final(self.root, self.raw_dir)
            self.assertEqual(report, evaluate_final(self.root, self.raw_dir))
        self.assertEqual(verify_freeze_v2(self.root), before)
        self.assertEqual(report['split'], 'v2_final')
        self.assertEqual(report['query_count'], 24)
        self.assertTrue(report['final_v2_executed'])
        self.assertTrue(report['v1_preserved'])
        self.assertEqual(set(report['methods']), {'literal_v1', 'tfidf_v1', 'bm25'})
        for result in report['methods'].values():
            self.assertEqual(result['positive_hits'], 18)
            self.assertEqual(result['mrr_at_5'], 1)
            self.assertEqual(result['false_positive_queries'], 0)
        self.assertEqual(report['configuration']['bm25'], BM25)
        rendered = json.dumps(report)
        for excluded in ('threshold_grid', 'candidate_min_score', 'timings', 'ruby emerald', 'phantom'):
            self.assertNotIn(excluded, rendered)
        for result in report['results']:
            for method in report['methods']:
                self.assertTrue(all(set(row) == {'id', 'score'} for row in result[method]))
        queries = [{'id': 'a', 'answerable': True, 'relevant_ids': ['known']},
                   {'id': 'b', 'answerable': True, 'relevant_ids': ['other']},
                   {'id': 'c', 'answerable': False, 'relevant_ids': []}]
        result = metrics(queries, {'a': [{'id': 'x'}, {'id': 'known'}], 'b': [], 'c': [{'id': 'x'}]})
        self.assertEqual(result['mrr_at_5'], 0.25)
        self.assertEqual(result['known_hit_at_5'], 0.5)
        self.assertEqual(result['positive_queries_without_results'], 1)
        self.assertEqual(result['false_positive_queries'], 1)

    def test_missing_positive_or_negative_reference_prevents_search(self):
        for removed in ('synthetic:1', 'synthetic:2'):
            source = [p for p in self.paragraphs if p['id'] != removed]
            with self.subTest(removed=removed), patch('sherlock_search.v2_final.prepare_corpus', return_value=(source, self.corpus)):
                with patch('sherlock_search.v2_final.literal_search') as search:
                    with self.assertRaisesRegex(ValueError, 'Referência'):
                        evaluate_final(self.root, self.raw_dir)
                    search.assert_not_called()

    def test_changed_inputs_and_corpus_during_search_are_detected(self):
        for relative in ('reports/v2/development.approved.json', 'data/raw/synthetic.txt', 'evaluation/v2/freeze.json'):
            target = self.root / relative
            original = target.read_bytes()
            def mutate(*args):
                target.write_bytes(original + b' ')
                return []
            with self.subTest(relative=relative), patch('sherlock_search.v2_final.prepare_corpus', return_value=(self.paragraphs, self.corpus)):
                with patch('sherlock_search.v2_final.literal_search', side_effect=mutate):
                    with self.assertRaises(ValueError):
                        evaluate_final(self.root, self.raw_dir)
            target.write_bytes(original)

    def test_frozen_outputs_and_aliases_are_protected(self):
        protected = self.root / 'reports/v2/development.approved.json'
        with self.assertRaises(ValueError):
            validate_final_output(self.root, protected, self.snapshot)
        alias = protected.with_name('alias.json')
        alias.symlink_to(protected)
        with self.assertRaises(ValueError):
            validate_final_output(self.root, alias, self.snapshot)
        hardlink = protected.with_name('hardlink.json')
        hardlink.hardlink_to(protected)
        with self.assertRaises(ValueError):
            validate_final_output(self.root, hardlink, self.snapshot)
        with self.assertRaises(ValueError):
            validate_final_output(self.root, self.root / 'evaluation/result.json', self.snapshot)
        self.assertEqual(validate_final_output(self.root, self.root / 'reports/v2/final.json', self.snapshot),
                         self.root / 'reports/v2/final.json')

    def test_cli_rejects_overwriting_frozen_report_before_evaluation(self):
        arguments = ['v2-final', '--root', str(self.root), '--output', 'reports/v2/development.approved.json']
        with patch('sys.argv', arguments), patch('sherlock_search.v2_final.evaluate_final') as evaluate:
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                main()
            self.assertEqual(raised.exception.code, 2)
            evaluate.assert_not_called()
        with patch('sys.argv', ['v2-final', '--min-score', '0']):
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                main()
            self.assertEqual(raised.exception.code, 2)
        with patch('sys.argv', ['v2-final', '--root', str(self.root)]):
            with patch('sherlock_search.v2_final.prepare_corpus', return_value=(self.paragraphs, self.corpus)):
                with redirect_stdout(io.StringIO()):
                    main()
        report = json.loads((self.root / 'reports/v2/final.json').read_text())
        self.assertTrue(report['final_v2_executed'])
        self.assertEqual(verify_freeze_v2(self.root), self.snapshot)


if __name__ == '__main__':
    unittest.main()
