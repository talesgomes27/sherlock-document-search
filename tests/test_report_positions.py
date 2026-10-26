"""Check chart positions against saved rankings and published aggregate measures."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from plot_query_positions import query_positions


class QueryPositionsTests(unittest.TestCase):
    def test_rank_is_first_known_hit_within_five_and_negatives_are_excluded(self):
        report = {'results': [
            {'id': 'positive', 'answerable': True, 'known_relevant_ids': ['b', 'c'],
             'method': [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}]},
            {'id': 'outside', 'answerable': True, 'known_relevant_ids': ['b'],
             'method': [{'id': 'a'}] * 5 + [{'id': 'b'}]},
            {'id': 'empty', 'answerable': True, 'known_relevant_ids': ['b'], 'method': []},
            {'id': 'negative', 'answerable': False},
        ]}
        self.assertEqual(query_positions(report, [('method', 'Example')]),
                         (['positive', 'outside', 'empty'], [[2], [0], [0]]))

    def test_positions_reproduce_published_hits_and_mrr_in_both_studies(self):
        for path, methods in [
            ('reports/m4_final.json', [('literal', 'Literal'), ('tfidf', 'TF-IDF')]),
            ('reports/v2/final.json', [('literal_v1', 'Literal'), ('tfidf_v1', 'TF-IDF'), ('bm25', 'BM25')]),
        ]:
            report = json.loads((ROOT / path).read_text())
            ids, rows = query_positions(report, methods)
            metrics = report.get('methods', report)
            for column, (key, _) in enumerate(methods):
                with self.subTest(study=path, method=key):
                    ranks = [row[column] for row in rows]
                    self.assertEqual(len(ids), metrics[key]['positive_queries'])
                    self.assertEqual(sum(rank > 0 for rank in ranks), metrics[key]['positive_hits'])
                    if 'mrr_at_5' in metrics[key]:
                        self.assertAlmostEqual(sum(1 / rank if rank else 0 for rank in ranks) / len(ranks),
                                               metrics[key]['mrr_at_5'])

    def test_presentation_copies_preserve_original_code_and_outputs(self):
        for version, original_name in [('v1', 'sherlock_document_search.ipynb'),
                                       ('v2', 'sherlock_document_search_v2.ipynb')]:
            with self.subTest(study=version):
                original = json.loads((ROOT / 'notebooks' / original_name).read_text())
                presentation = json.loads((ROOT / f'notebooks/portfolio/sherlock_document_search_{version}.ipynb').read_text())
                old_code = [cell for cell in original['cells'] if cell['cell_type'] == 'code']
                new_code = [cell for cell in presentation['cells'] if cell['cell_type'] == 'code']
                added = [cell for cell in new_code if 'presentation-only-chart' in cell.get('metadata', {}).get('tags', [])]
                self.assertEqual(len(added), 1)
                self.assertEqual(old_code, [cell for cell in new_code if cell not in added])
