import json
from pathlib import Path
import tempfile
import unittest

from sherlock_search.query_review import prepare_reviews


class QueryReviewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.queries = self.root / "evaluation"
        self.queries.mkdir()
        self.paragraphs = [{
            "id": "synthetic.txt:2-3", "filename": "synthetic.txt", "title": "Synthetic",
            "line_start": 2, "line_end": 3, "text": "A synthetic passage for human review.",
        }]
        for split, prefix, count in [("development", "dev", 10), ("final", "final", 20)]:
            rows = [{
                "id": f"{prefix}-{i:02}", "query": f"Synthetic question {prefix} {i}?",
                "query_type": "question", "answerable": i != count,
                "relevant_ids": ["synthetic.txt:2-3"] if i != count else [],
                "rationale": "Synthetic proposal, not an actual corpus judgment.",
                "review_status": "pending",
            } for i in range(1, count + 1)]
            (self.queries / f"{split}.json").write_text(json.dumps(rows), encoding="utf-8")

    def change_first(self, **changes):
        path = self.queries / "final.json"
        rows = json.loads(path.read_text())
        rows[0].update(changes)
        path.write_text(json.dumps(rows), encoding="utf-8")

    def test_separate_review_files_and_pending_status_without_retrieval(self):
        output = self.root / "reviews"
        summary = prepare_reviews(self.queries, self.paragraphs, output)
        self.assertEqual(summary["development"]["queries"], 10)
        self.assertEqual(summary["final"]["queries"], 20)
        self.assertEqual(summary["final"]["approved"], 0)
        self.assertIn("final-01", (output / "final.md").read_text())
        self.assertNotIn("final-01", (output / "development.md").read_text())
        self.assertIn("synthetic.txt:2-3", (output / "development.md").read_text())
        self.assertEqual(len(summary["final"]["sha256"]), 64)

    def test_unknown_reference_rejected_before_writing_reviews(self):
        self.change_first(relevant_ids=["synthetic.txt:99-100"])
        output = self.root / "reviews"
        with self.assertRaisesRegex(ValueError, "referência"):
            prepare_reviews(self.queries, self.paragraphs, output)
        self.assertFalse(output.exists())

    def test_cross_split_duplicate_and_invalid_negative_label_rejected(self):
        self.change_first(query="  SYNTHETIC question dev 1?  ")
        with self.assertRaisesRegex(ValueError, "duplicada"):
            prepare_reviews(self.queries, self.paragraphs, self.root / "reviews")
        self.change_first(query="Unique question?", answerable=False)
        with self.assertRaisesRegex(ValueError, "rótulo"):
            prepare_reviews(self.queries, self.paragraphs, self.root / "reviews")

    def test_invalid_review_status_cannot_be_counted_as_approved(self):
        self.change_first(review_status="automatic")
        with self.assertRaisesRegex(ValueError, "status"):
            prepare_reviews(self.queries, self.paragraphs, self.root / "reviews")

    def test_invalid_field_types_raise_validation_error(self):
        self.change_first(query_type=[])
        with self.assertRaisesRegex(ValueError, "tipo"):
            prepare_reviews(self.queries, self.paragraphs, self.root / "reviews")
        self.change_first(query_type="question", review_status=[])
        with self.assertRaisesRegex(ValueError, "status"):
            prepare_reviews(self.queries, self.paragraphs, self.root / "reviews")


if __name__ == "__main__":
    unittest.main()
