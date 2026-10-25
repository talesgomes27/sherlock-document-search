import hashlib
from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sherlock_search.development import choose_threshold, load_development, main, summarize, verify_freeze


class DevelopmentTests(unittest.TestCase):
    def test_rates_use_answerable_and_unanswerable_denominators(self):
        queries = [
            {"id": "a", "answerable": True, "relevant_ids": ["p1"]},
            {"id": "b", "answerable": True, "relevant_ids": ["p2"]},
            {"id": "c", "answerable": False, "relevant_ids": []},
        ]
        predictions = {"a": [{"id": "p1"}], "b": [], "c": [{"id": "p3"}]}
        result = summarize(queries, predictions)
        self.assertEqual(result["positive_hits"], 1)
        self.assertEqual(result["positive_queries"], 2)
        self.assertEqual(result["known_hit_at_5"], 0.5)
        self.assertEqual(result["false_positive_queries"], 1)
        self.assertEqual(result["negative_queries"], 1)
        self.assertEqual(result["false_positive_rate"], 1.0)
        self.assertEqual(result["balanced_utility"], 0.25)

    def test_threshold_preserves_baseline_hits_then_minimizes_false_positives(self):
        candidates = [{"min_score": 0.3, "positive_hits": 0, "false_positive_rate": 0},
                      {"min_score": 0.2, "positive_hits": 2, "false_positive_rate": 0.5},
                      {"min_score": 0.1, "positive_hits": 2, "false_positive_rate": 0.5},
                      {"min_score": 0, "positive_hits": 2, "false_positive_rate": 1}]
        self.assertEqual(choose_threshold(candidates), 0.1)

    def test_development_requires_both_label_classes(self):
        with self.assertRaisesRegex(ValueError, "classes"):
            summarize([{"id": "a", "answerable": True, "relevant_ids": ["p"]}], {"a": []})

    def test_loader_requires_reviewed_snapshot_and_never_needs_final_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = [{"id": f"dev-{i:02}", "query": f"question {i}", "review_status": "approved",
                     "answerable": i != 10, "relevant_ids": ["p1"] if i != 10 else []}
                    for i in range(1, 11)]
            path = root / "development.json"
            path.write_text(json.dumps(rows), encoding="utf-8")
            self.write_manifest(root, path)
            self.assertEqual(len(load_development(root)), 10)
            path.write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                load_development(root)
            rows[0]["review_status"] = "pending"
            path.write_text(json.dumps(rows), encoding="utf-8")
            self.write_manifest(root, path)
            with self.assertRaisesRegex(ValueError, "aprovadas"):
                load_development(root)

    def test_invalid_json_types_do_not_change_label_denominators(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = [{"id": f"dev-{i:02}", "query": "question", "review_status": "approved",
                     "answerable": i != 10, "relevant_ids": ["p1"] if i != 10 else []}
                    for i in range(1, 11)]
            for invalid in [{"answerable": "false"}, {"query": []}, {"relevant_ids": "p1"}, {"relevant_ids": []}]:
                changed = [dict(row) for row in rows]
                changed[0].update(invalid)
                path = root / "development.json"
                path.write_text(json.dumps(changed), encoding="utf-8")
                self.write_manifest(root, path)
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    load_development(root)
            path.write_text(json.dumps([0] + rows[1:]), encoding="utf-8")
            self.write_manifest(root, path)
            with self.assertRaises(ValueError):
                load_development(root)

    def test_cli_refuses_output_in_input_directories_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, queries = root / "raw", root / "evaluation"
            raw.mkdir()
            queries.mkdir()
            for output in [queries / "development.json", raw / "source.txt"]:
                output.write_text("preserve", encoding="utf-8")
                argv = ["development", "--raw-dir", str(raw), "--queries-dir", str(queries), "--output", str(output)]
                with patch("sys.argv", argv), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    main()
                self.assertEqual(error.exception.code, 2)
                self.assertEqual(output.read_text(), "preserve")

    def test_freeze_checks_opaque_bytes_and_detects_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "evaluation").mkdir()
            source = root / "source.py"
            source.write_text("original", encoding="utf-8")
            snapshot = {"file_sha256": {"source.py": hashlib.sha256(source.read_bytes()).hexdigest()}}
            (root / "evaluation/m3_freeze.json").write_text(json.dumps(snapshot), encoding="utf-8")
            self.assertEqual(verify_freeze(root), snapshot)
            source.write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "congelado"):
                verify_freeze(root)

    def test_freeze_rejects_paths_outside_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "evaluation").mkdir()
            snapshot = {"file_sha256": {"../outside": "invalid"}}
            (root / "evaluation/m3_freeze.json").write_text(json.dumps(snapshot), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "caminho"):
                verify_freeze(root)

    def test_empty_or_malformed_freeze_cannot_be_reported_as_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "evaluation").mkdir()
            for snapshot in [[], {}, {"file_sha256": []}, {"file_sha256": {}}]:
                (root / "evaluation/m3_freeze.json").write_text(json.dumps(snapshot), encoding="utf-8")
                with self.subTest(snapshot=snapshot), self.assertRaises(ValueError):
                    verify_freeze(root)

    @staticmethod
    def write_manifest(root, path):
        (root / "split_manifest.json").write_text(json.dumps({"splits": {"development": {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "approved": 10,
        }}}), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
