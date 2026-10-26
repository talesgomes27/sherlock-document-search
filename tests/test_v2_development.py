from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sherlock_search import v2_development as v2


class V2DevelopmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'evaluation/v2').mkdir(parents=True)
        self.protocol = {'development': {'queries': 36, 'answerable': 27, 'unanswerable': 9,
                         'query_types': {'exact': 9, 'paraphrase': 9, 'context': 9, 'unanswerable': 9}}}
        self.queries = [dict(id=f'v2-dev-{i+1:02}', query=f'synthetic {i}', answerable=i < 27,
                            relevant_ids=['a.txt:1'] if i < 27 else [], rationale='Synthetic fixture',
                            query_type=['exact', 'paraphrase', 'context', 'unanswerable'][i//9],
                            review_status='proposed', negative_verification=dict(method='read', kind='missing_detail', finding='not specified', scope='synthetic', uncertainty='proposed', evidence_ids=['a.txt:1'])) for i in range(36)]
        (self.root / 'evaluation/v2/protocol.json').write_text(json.dumps(self.protocol))
        self.write_queries()

    def write_queries(self):
        (self.root / 'evaluation/v2/development.json').write_text(json.dumps(self.queries))

    def test_proposals_require_explicit_exploration(self):
        with self.assertRaisesRegex(ValueError, 'proposed|propost'):
            v2.load_development(self.root)
        self.assertEqual(v2.load_development(self.root, allow_proposed=True), self.queries)
        for row in self.queries:
            row['review_status'] = 'approved'
        self.write_queries()
        self.assertEqual(v2.load_development(self.root), self.queries)

    def test_loader_rejects_changed_ids_labels_types_and_references(self):
        bad = [('id', 'v2-final-01'), ('answerable', 1), ('relevant_ids', []),
               ('query', ' '), ('query_type', 'unknown'), ('review_status', 'unknown')]
        for key, value in bad:
            with self.subTest(key=key):
                before = self.queries[0][key]
                self.queries[0][key] = value
                self.write_queries()
                with self.assertRaises(ValueError):
                    v2.load_development(self.root, allow_proposed=True)
                self.queries[0][key] = before

    def test_loader_never_opens_a_final_query_file(self):
        original = Path.read_text
        opened = []
        def read(path, *args, **kwargs):
            opened.append(path)
            if 'holdout' in str(path) or path.name.startswith('final'):
                raise AssertionError('Reserved data opened')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', read):
            v2.load_development(self.root, allow_proposed=True)
        self.assertEqual({path.name for path in opened}, {'protocol.json', 'development.json'})

    def test_selection_is_fixed_and_may_trade_hits_for_abstention(self):
        rows = [dict(min_score=0, positive_queries=2, positive_hits=2, negative_queries=2, false_positive_queries=2),
                dict(min_score=1, positive_queries=2, positive_hits=1, negative_queries=2, false_positive_queries=0),
                dict(min_score=2, positive_queries=2, positive_hits=1, negative_queries=2, false_positive_queries=0)]
        self.assertEqual(v2.choose_threshold(rows), 1)
        rows[0]['false_positive_queries'] = 0
        self.assertEqual(v2.choose_threshold(rows), 0)

    def test_comparison_keeps_baselines_and_marks_provisional_candidate(self):
        paragraphs = [dict(id='a.txt:1', filename='a.txt', line_start=1, line_end=1, text='ruby emerald', title='A'),
                      dict(id='b.txt:1', filename='b.txt', line_start=1, line_end=1, text='sapphire diamond', title='B')]
        queries = [dict(id='v2-dev-01', query='ruby', answerable=True, relevant_ids=['a.txt:1'], review_status='proposed'),
                   dict(id='v2-dev-02', query='helicopter', answerable=False, relevant_ids=[], review_status='proposed')]
        protocol = {'bm25': {'k1': 1.2, 'b': .75}, 'thresholds': [0, 1, 32], 'selection_rule': 'maximize_balanced_utility_then_minimize_false_positive_rate_then_minimize_threshold'}
        report = v2.compare_development(paragraphs, queries, protocol)
        self.assertEqual(report['split'], 'v2_development')
        self.assertEqual(report['annotation_status'], 'proposed')
        self.assertTrue(report['candidate_provisional'])
        for method in ['literal_v1', 'tfidf_v1', 'bm25_uncut', 'bm25_candidate']:
            self.assertEqual(report[method]['positive_hits'], 1)
            self.assertEqual(report[method]['false_positive_queries'], 0)
            self.assertEqual(report[method]['mrr_at_5'], 1)
        self.assertEqual(report['candidate_min_score'], 0)
        self.assertEqual(len(report['threshold_grid']), 3)
        with self.assertRaisesRegex(ValueError, 'Referência'):
            queries[0]['relevant_ids'] = ['missing']
            v2.compare_development(paragraphs, queries, protocol)

    def test_output_cannot_overwrite_inputs_v1_symlinks_or_hardlinks(self):
        allowed = self.root / 'reports/v2/result.json'
        self.assertEqual(v2.validate_output(self.root, allowed), allowed)
        for path in [self.root/'reports/m4_final.json', self.root/'evaluation/v2/development.json', self.root/'data/raw/a.txt']:
            with self.assertRaises(ValueError):
                v2.validate_output(self.root, path)
        allowed.parent.mkdir(parents=True)
        source = self.root / 'evaluation/v2/development.json'
        allowed.symlink_to(source)
        with self.assertRaises(ValueError):
            v2.validate_output(self.root, allowed)
        allowed.unlink()
        allowed.hardlink_to(source)
        with self.assertRaises(ValueError):
            v2.validate_output(self.root, allowed)

    def test_preservation_detects_changed_file(self):
        source = self.root / 'old.py'
        source.write_text('original')
        import hashlib
        manifest = {'file_sha256': {'old.py': hashlib.sha256(source.read_bytes()).hexdigest()}}
        (self.root/'evaluation/v2/v1_preservation.json').write_text(json.dumps(manifest))
        v2.verify_preservation(self.root)
        source.write_text('changed')
        with self.assertRaisesRegex(ValueError, 'v1'):
            v2.verify_preservation(self.root)


    def test_rational_tie_does_not_depend_on_float_rounding(self):
        rows = [dict(min_score=0, positive_hits=3, positive_queries=27, false_positive_queries=2, negative_queries=9),
                dict(min_score=1, positive_hits=0, positive_queries=27, false_positive_queries=1, negative_queries=9)]
        self.assertEqual(v2.choose_threshold(rows), 1)

    def test_negative_evidence_requires_structured_content(self):
        for value in (True, 1, [], 'text', {}, {'method': 'read'}):
            with self.subTest(value=value):
                self.queries[27]['negative_verification'] = value
                self.write_queries()
                with self.assertRaises(ValueError):
                    v2.load_development(self.root, allow_proposed=True)

    def test_protocol_counts_require_integer_types(self):
        self.protocol['development']['queries'] = 36.0
        (self.root/'evaluation/v2/protocol.json').write_text(json.dumps(self.protocol))
        with self.assertRaises(ValueError):
            v2.load_development(self.root, allow_proposed=True)

    def test_cli_refuses_output_before_any_evaluation(self):
        with patch('sys.argv', ['v2', '--root', str(self.root), '--output', 'evaluation/v2/development.json']), patch.object(v2, 'run_development') as run, redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                v2.main()
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
