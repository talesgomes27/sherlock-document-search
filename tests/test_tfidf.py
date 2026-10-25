import copy
from contextlib import redirect_stdout
import io
import json
import math
import unittest
from unittest.mock import patch

from sherlock_search.tfidf import TfidfSearch
from sherlock_search.__main__ import main

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def paragraph(filename, line, text, *, end=None):
    return {"id": f"{filename}:{line}", "filename": filename,
            "line_start": line, "line_end": line if end is None else end,
            "text": text, "title": "Original title", "extra": "preserved"}


class TfidfSearchTests(unittest.TestCase):
    def test_cli_labels_cosine_score_and_empty_query(self):
        source = [paragraph("a.txt", 1, "ruby emerald")]
        for query, expected in [("ruby", "similaridade de cosseno"), ("", "Nenhuma correspondência TF-IDF")]:
            with self.subTest(query=query), patch("sys.argv", ["sherlock", "--method", "tfidf", "--query", query]):
                with patch("sherlock_search.__main__.prepare_corpus", return_value=(source, {})):
                    buffer = io.StringIO()
                    with redirect_stdout(buffer):
                        main()
                    self.assertIn(expected, buffer.getvalue())
                    self.assertNotIn("ocorrências:", buffer.getvalue())

    def test_matches_default_sklearn_cosine_on_whole_corpus(self):
        source = [paragraph("a.txt", 1, "ruby ruby emerald"),
                  paragraph("b.txt", 2, "emerald sapphire"),
                  paragraph("c.txt", 3, "ruby diamond")]
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([p["text"] for p in source])
        expected = cosine_similarity(vectorizer.transform(["ruby emerald"]), matrix)[0]
        expected_by_id = {p["id"]: score for p, score in zip(source, expected)}
        engine = TfidfSearch(source, min_score=0)
        results = engine.search("ruby emerald")
        self.assertEqual([p["id"] for p in results],
                         [p["id"] for p in sorted(source, key=lambda p: -expected_by_id[p["id"]])])
        for result in results:
            self.assertIsInstance(result["score"], float)
            self.assertAlmostEqual(result["score"], expected_by_id[result["id"]])
        filtered = engine.search("ruby emerald", filename="b.txt")
        self.assertAlmostEqual(filtered[0]["score"], expected[1])

    def test_fit_once_and_reuse_for_queries_and_filters(self):
        original = TfidfVectorizer.fit_transform
        with patch.object(TfidfVectorizer, "fit_transform", autospec=True, side_effect=original) as fit:
            engine = TfidfSearch([paragraph("a.txt", 1, "ruby emerald")], min_score=0)
            engine.search("ruby")
            engine.search("emerald", filename="a.txt")
        self.assertEqual(fit.call_count, 1)

    def test_top_five_and_all_tie_breakers(self):
        source = [paragraph("b.txt", 1, "ruby")]
        source += [paragraph("a.txt", line, "ruby") for line in range(7, 1, -1)]
        source += [paragraph("a.txt", 1, "ruby", end=3), paragraph("a.txt", 1, "ruby", end=2)]
        results = TfidfSearch(source, min_score=0).search("ruby")
        self.assertEqual([(p["filename"], p["line_start"], p["line_end"]) for p in results],
                         [("a.txt", 1, 2), ("a.txt", 1, 3), ("a.txt", 2, 2), ("a.txt", 3, 3), ("a.txt", 4, 4)])

    def test_filter_applies_before_top_five(self):
        source = [paragraph("a.txt", line, "ruby") for line in range(1, 9)]
        source.append(paragraph("b.txt", 1, "ruby emerald"))
        results = TfidfSearch(source, min_score=0).search("ruby", filename="b.txt")
        self.assertEqual([p["filename"] for p in results], ["b.txt"])

    def test_threshold_is_inclusive_and_zero_scores_are_always_excluded(self):
        source = [paragraph("a.txt", 1, "ruby"), paragraph("b.txt", 1, "emerald")]
        self.assertEqual(len(TfidfSearch(source, min_score=1).search("ruby")), 1)
        self.assertEqual(len(TfidfSearch(source, min_score=0).search("ruby")), 1)
        self.assertEqual(TfidfSearch(source, min_score=0.8).search("ruby emerald"), [])

    def test_metadata_and_inputs_are_preserved(self):
        source = [paragraph("a.txt", 4, "ruby emerald")]
        before = copy.deepcopy(source)
        result = TfidfSearch(source, min_score=0).search("ruby")[0]
        self.assertEqual(source, before)
        self.assertIsNot(result, source[0])
        self.assertEqual({k: result[k] for k in before[0]}, before[0])

    def test_empty_queries_stopwords_punctuation_and_oov(self):
        engine = TfidfSearch([paragraph("a.txt", 1, "ruby emerald")], min_score=0)
        for query in ["", " \t\n", "...!*", "the and is", "sapphire"]:
            with self.subTest(query=query):
                self.assertEqual(engine.search(query), [])

    def test_empty_corpus_and_empty_vocabulary(self):
        for source in [[], [paragraph("a.txt", 1, "the and ...")], [paragraph("a.txt", 1, "")]]:
            with self.subTest(source=source):
                engine = TfidfSearch(source, min_score=0)
                self.assertEqual(engine.search("ruby"), [])

    def test_unknown_filename_matches_literal_error_even_for_empty_query(self):
        for source in [[], [paragraph("a.txt", 1, "the and")]]:
            engine = TfidfSearch(source, min_score=0)
            with self.assertRaisesRegex(ValueError, "^Obra desconhecida: unknown.txt$"):
                engine.search("", filename="unknown.txt")

    def test_invalid_thresholds_have_clear_errors(self):
        for value in [-0.1, 1.1, math.nan, math.inf, -math.inf, "0.5", True, {}]:
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "min_score"):
                TfidfSearch([], min_score=value)

    def test_default_threshold_is_loaded_from_adjacent_config(self):
        with patch("sherlock_search.tfidf.Path") as path:
            config = path.return_value.with_name.return_value
            config.read_text.return_value = json.dumps({"min_score": 0.9})
            engine = TfidfSearch([paragraph("a.txt", 1, "ruby emerald")])
        path.return_value.with_name.assert_called_once_with("tfidf_config.json")
        config.read_text.assert_called_once_with(encoding="utf-8")
        self.assertEqual(engine.search("ruby"), [])

    def test_explicit_threshold_does_not_read_config(self):
        with patch("sherlock_search.tfidf.Path", side_effect=AssertionError("unexpected config read")):
            TfidfSearch([], min_score=0)

    def test_invalid_config_has_clear_error(self):
        for contents in ["invalid json", "{}", "[]", '{"min_score": null}', '{"min_score": 2}']:
            with self.subTest(contents=contents), patch("sherlock_search.tfidf.Path") as path:
                path.return_value.with_name.return_value.read_text.return_value = contents
                with self.assertRaisesRegex(ValueError, "min_score"):
                    TfidfSearch([])
        with patch("sherlock_search.tfidf.Path") as path:
            path.return_value.with_name.return_value.read_text.side_effect = FileNotFoundError("missing")
            with self.assertRaisesRegex(ValueError, "min_score"):
                TfidfSearch([])


if __name__ == "__main__":
    unittest.main()
