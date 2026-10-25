import copy
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sherlock_search.__main__ import main
from sherlock_search.corpus import prepare_corpus
from sherlock_search.search import literal_search


def paragraph(filename, line, text):
    return {
        "id": f"{filename}:{line}-{line}", "filename": filename,
        "title": filename.removesuffix(".txt"), "line_start": line,
        "line_end": line, "text": text,
    }


class LiteralSearchTests(unittest.TestCase):
    def test_complete_words_case_insensitive_and_occurrence_score(self):
        source = [paragraph("a.txt", 1, "Holmes met HOLMES. Holmesian left.")]
        results = literal_search(source, "holmes")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["score"], 2)
        self.assertEqual(literal_search(source, "olm"), [])

    def test_phrase_whitespace_and_punctuation_are_literal(self):
        source = [paragraph("a.txt", 1, "Dr. Watson visited Baker    Street; DrX Watson left.")]
        self.assertEqual(literal_search(source, "  BAKER \n Street ")[0]["score"], 1)
        self.assertEqual(literal_search(source, "Dr. Watson")[0]["score"], 1)
        self.assertEqual(literal_search(source, "Dr.*Watson"), [])

    def test_empty_punctuation_and_absent_query_return_no_results(self):
        source = [paragraph("a.txt", 1, "Holmes waits.")]
        for query in ["", " \t\n", ".*", "absentword"]:
            with self.subTest(query=query):
                self.assertEqual(literal_search(source, query), [])

    def test_fixed_top_five_and_deterministic_ties(self):
        source = [paragraph("b.txt", 1, "signal signal")]
        source += [paragraph("a.txt", line, "signal") for line in range(7, 0, -1)]
        results = literal_search(source, "signal")
        self.assertEqual(len(results), 5)
        self.assertEqual([p["id"] for p in results], ["b.txt:1-1", "a.txt:1-1", "a.txt:2-2", "a.txt:3-3", "a.txt:4-4"])

    def test_filter_applies_before_top_five_and_unknown_book_is_rejected(self):
        source = [paragraph("a.txt", line, "signal signal") for line in range(1, 8)]
        source += [paragraph("b.txt", 1, "signal")]
        self.assertEqual(literal_search(source, "signal", filename="b.txt")[0]["filename"], "b.txt")
        with self.assertRaisesRegex(ValueError, "Obra"):
            literal_search(source, "signal", filename="unknown.txt")

    def test_results_preserve_metadata_without_mutating_source(self):
        source = [paragraph("a.txt", 7, "message")]
        before = copy.deepcopy(source)
        result = literal_search(source, "message")[0]
        self.assertEqual(source, before)
        for key, value in before[0].items():
            self.assertEqual(result[key], value)

    def test_phrase_occurrences_do_not_overlap(self):
        self.assertEqual(literal_search([paragraph("a.txt", 1, "a a a")], "a a")[0]["score"], 1)

    def test_cli_search_preserves_preparation_outputs(self):
        source = [paragraph("a.txt", 7, "Holmes waits.")]
        for query, expected in [("Holmes", "a.txt:7-7"), ("missing", "Nenhuma correspondência")]:
            with self.subTest(query=query), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "not-written"
                buffer = io.StringIO()
                with patch("sys.argv", ["sherlock_search", "--query", query, "--output-dir", str(output)]):
                    with patch("sherlock_search.__main__.prepare_corpus", return_value=(source, {})):
                        with redirect_stdout(buffer):
                            main()
                self.assertIn(expected, buffer.getvalue())
                self.assertFalse(output.exists())


REAL_RAW_DIR = Path(os.environ.get("SHERLOCK_RAW_DIR", "data/raw"))


@unittest.skipUnless(REAL_RAW_DIR.is_dir(), "Real corpus not available")
class LiteralCorpusIntegrationTests(unittest.TestCase):
    def test_development_queries_preserve_top_five_and_source_contract(self):
        paragraphs, _ = prepare_corpus(REAL_RAW_DIR)
        source_by_id = {p["id"]: p for p in paragraphs}
        path = Path(__file__).resolve().parents[1] / "evaluation" / "development.json"
        queries = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(queries), 10)
        for query in queries:
            with self.subTest(query=query["id"]):
                results = literal_search(paragraphs, query["query"])
                self.assertLessEqual(len(results), 5)
                for result in results:
                    self.assertGreater(result["score"], 0)
                    for key, value in source_by_id[result["id"]].items():
                        self.assertEqual(result[key], value)

    def test_development_term_returns_original_references_in_selected_book(self):
        paragraphs, _ = prepare_corpus(REAL_RAW_DIR)
        source_by_id = {p["id"]: p for p in paragraphs}
        results = literal_search(paragraphs, "Cyanea", filename="the_case-book_of_sherlock_holmes.txt")
        self.assertTrue(results)
        self.assertLessEqual(len(results), 5)
        for result in results:
            self.assertEqual(result["filename"], "the_case-book_of_sherlock_holmes.txt")
            for key, value in source_by_id[result["id"]].items():
                self.assertEqual(result[key], value)


if __name__ == "__main__":
    unittest.main()
