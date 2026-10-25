import copy
from contextlib import ExitStack, redirect_stderr
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sherlock_search import final_evaluation as final


class FinalEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'evaluation').mkdir()
        self.raw = self.root / 'raw'
        self.raw.mkdir()
        self.rows = [dict(id=f'final-{i:02}', query=f'synthetic {i}', review_status='approved',
                          answerable=i <= 16, relevant_ids=['p1'] if i <= 16 else [])
                     for i in range(1, 21)]
        self.snapshot = {'file_sha256': {'reports/m3_development.json': 'frozen'},
                         'runtime_versions': {'python': '3.11.17', 'scikit-learn': '1.9.1',
                                              'numpy': '2.4.6', 'scipy': '1.17.1'},
                         'tfidf': {'min_score': 0.0, 'vectorizer': 'frozen vectorizer'}}
        (self.root / 'evaluation/m3_freeze.json').write_text(json.dumps(self.snapshot))
        self.write_inputs()
        self.stack = self.enterContext(ExitStack())
        self.verify = self.stack.enter_context(patch.object(final, 'verify_freeze', return_value=self.snapshot))
        self.real_verify_sources = final.verify_sources
        self.stack.enter_context(patch.object(final, 'verify_sources'))
        self.stack.enter_context(patch.object(final, 'runtime_versions', return_value=self.snapshot['runtime_versions']))
        self.prepare = self.stack.enter_context(patch.object(final, 'prepare_corpus', return_value=(
            [{'id': 'p1', 'text': 'PRIVATE SOURCE TEXT'}], {'totals': {'files': 9, 'paragraphs': 1}, 'files': []})))
        self.index = self.stack.enter_context(patch.object(final, 'TfidfSearch'))
        self.index.return_value.min_score = 0.0
        self.index.return_value.search.return_value = [{'id': 'p1', 'score': 0.5, 'text': 'PRIVATE SOURCE TEXT'}]
        self.literal = self.stack.enter_context(patch.object(final, 'literal_search', return_value=[]))

    def write_inputs(self):
        (self.root / 'evaluation/final.json').write_text(json.dumps(self.rows))
        manifest = {'splits': {'final': {'queries': 20, 'answerable': 16, 'unanswerable': 4,
                                       'approved': 20, 'needs_changes': 0}}}
        (self.root / 'evaluation/split_manifest.json').write_text(json.dumps(manifest))

    def test_frozen_metrics_and_private_text_omission(self):
        report = final.evaluate_final(self.root, self.raw)
        self.assertEqual(report['query_count'], 20)
        self.assertEqual(report['tfidf']['known_hit_at_5'], 1)
        self.assertEqual(report['tfidf']['false_positive_rate'], 1)
        self.assertEqual(report['tfidf']['balanced_utility'], 0.5)
        self.assertEqual(report['literal']['balanced_utility'], 0.5)
        self.assertEqual(report['selected_min_score'], 0.0)
        self.assertEqual(report['corpus']['totals']['files'], 9)
        self.assertNotIn('PRIVATE SOURCE TEXT', json.dumps(report))
        self.assertNotIn('threshold_grid', report)
        self.assertEqual(report['results'][0]['tfidf'], [{'id': 'p1', 'score': 0.5}])
        self.index.assert_called_once_with(self.prepare.return_value[0])
        self.assertEqual(self.index.return_value.search.call_count, 20)
        self.assertEqual(self.verify.call_count, 2)
        self.assertEqual(report, final.evaluate_final(self.root, self.raw))

    def test_runtime_mismatch_aborts_before_corpus_or_search(self):
        for key, value in [('python', '3.11.16'), ('scikit-learn', '1.9.0'), ('numpy', '2.0'), ('scipy', '1.0')]:
            versions = dict(self.snapshot['runtime_versions'], **{key: value})
            with self.subTest(key=key), patch.object(final, 'runtime_versions', return_value=versions):
                with self.assertRaisesRegex(ValueError, 'runtime'):
                    final.evaluate_final(self.root, self.raw)
        self.prepare.assert_not_called()
        self.index.assert_not_called()

    def test_wrong_pinned_python_cannot_be_accepted_by_matching_runtime(self):
        self.snapshot['runtime_versions']['python'] = '3.12.0'
        with self.assertRaisesRegex(ValueError, 'runtime'):
            final.evaluate_final(self.root, self.raw)
        self.index.assert_not_called()

    def test_invalid_queries_abort_before_search(self):
        original = copy.deepcopy(self.rows)
        for invalid in [{'answerable': 1}, {'relevant_ids': 'p1'}, {'relevant_ids': ['p1', 'p1']},
                        {'relevant_ids': [1]}, {'relevant_ids': []}, {'query': []}, {'query': '  '},
                        {'review_status': 'pending'}, {'id': 'final-99'}]:
            self.rows = copy.deepcopy(original)
            self.rows[0].update(invalid)
            self.write_inputs()
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                final.evaluate_final(self.root, self.raw)
        self.index.assert_not_called()

    def test_label_counts_and_manifest_are_fixed(self):
        self.rows[0].update(answerable=False, relevant_ids=[])
        self.write_inputs()
        with self.assertRaises(ValueError):
            final.evaluate_final(self.root, self.raw)
        self.index.assert_not_called()

    def test_missing_reference_aborts_before_search(self):
        self.rows[0]['relevant_ids'] = ['missing']
        self.write_inputs()
        with self.assertRaisesRegex(ValueError, 'Referência'):
            final.evaluate_final(self.root, self.raw)
        self.index.assert_not_called()

    def test_post_retrieval_freeze_change_rejects_report(self):
        self.verify.side_effect = [self.snapshot, ValueError('changed')]
        with self.assertRaisesRegex(ValueError, 'changed'):
            final.evaluate_final(self.root, self.raw)

    def test_cli_protects_frozen_sources_and_input_directories_before_search(self):
        for relative in ['evaluation/final.json', 'evaluation/m3_freeze.json',
                         'raw/source.txt', 'reports/m3_development.json']:
            output = self.root / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            before = output.read_bytes() if output.exists() else None
            argv = ['final_evaluation', '--root', str(self.root), '--raw-dir', str(self.raw), '--output', str(output)]
            with patch('sys.argv', argv), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                final.main()
            self.assertEqual(output.read_bytes() if output.exists() else None, before)
        self.index.assert_not_called()

    def test_manifest_metadata_must_keep_m2_counts_and_integer_types(self):
        path = self.root / 'evaluation/split_manifest.json'
        original = json.loads(path.read_text())
        for key, value in [('answerable', 15), ('unanswerable', 5), ('approved', 19), ('needs_changes', False)]:
            manifest = copy.deepcopy(original)
            manifest['splits']['final'][key] = value
            path.write_text(json.dumps(manifest))
            with self.subTest(key=key), self.assertRaises(ValueError):
                final.evaluate_final(self.root, self.raw)
        self.index.assert_not_called()

    def test_post_retrieval_corpus_change_rejects_report(self):
        source = self.raw / 'synthetic.txt'
        source.write_bytes(b'original')
        self.prepare.return_value[1]['files'] = [dict(filename=source.name, sha256=hashlib.sha256(b'original').hexdigest())]
        self.index.return_value.search.side_effect = lambda query: source.write_bytes(b'changed') and []
        with self.assertRaisesRegex(ValueError, 'Corpus alterado'):
            final.evaluate_final(self.root, self.raw)

    def test_post_retrieval_added_source_rejects_report(self):
        (self.raw / 'unexpected.txt').write_text('synthetic')
        with self.assertRaisesRegex(ValueError, 'Inventário'):
            final.evaluate_final(self.root, self.raw)

    def test_manifest_itself_cannot_change_during_retrieval(self):
        self.literal.side_effect = lambda *args: (self.root / 'evaluation/m3_freeze.json').write_text('{}') and []
        with self.assertRaisesRegex(ValueError, 'Manifesto congelado alterado'):
            final.evaluate_final(self.root, self.raw)

    def test_output_guard_follows_symlinks_and_hardlinks(self):
        protected = self.root / 'reports/m3_development.json'
        protected.parent.mkdir()
        protected.write_text('preserve')
        for kind in ['symlink', 'hardlink']:
            alias = self.root / (kind + '.json')
            if kind == 'symlink':
                alias.symlink_to(protected)
            else:
                alias.hardlink_to(protected)
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                final.validate_output(self.root, self.raw, alias.resolve(), self.snapshot)
            self.assertEqual(protected.read_text(), 'preserve')

    def test_cli_writes_deterministic_report_to_requested_destination(self):
        output = self.root / 'reports/m4_final.json'
        argv = ['final_evaluation', '--root', str(self.root), '--raw-dir', 'raw', '--output', 'reports/m4_final.json']
        with patch('sys.argv', argv), patch('sys.stdout', io.StringIO()):
            final.main()
            first = output.read_bytes()
            final.main()
        self.assertEqual(output.read_bytes(), first)
        self.assertEqual(json.loads(first)['query_count'], 20)

    def test_source_guard_detects_imported_module_mismatch(self):
        self.snapshot['file_sha256']['src/sherlock_search/tfidf.py'] = 'wrong hash'
        with self.assertRaisesRegex(ValueError, 'importado'):
            self.real_verify_sources(self.root, self.snapshot)


if __name__ == '__main__':
    unittest.main()
