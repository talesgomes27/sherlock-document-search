import copy
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
import io
import math
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

from scipy.sparse import issparse
from sklearn.feature_extraction.text import CountVectorizer

from sherlock_search.bm25 import BM25Search, main


def paragraph(filename, line, text, *, end=None):
    return {"id": f"{filename}:{line}", "filename": filename,
            "line_start": line, "line_end": line if end is None else end,
            "text": text, "title": "Synthetic title", "extra": "preserved"}


def oracle_scores(source, query, *, k1=1.2, b=0.75):
    # Synthetic inputs use only these English stopwords; no production analyzer or scoring code.
    def tokens(text):
        return [word for word in re.findall(r"\b\w\w+\b", text.lower())
                if word not in {"the", "and", "is"}]

    documents = [Counter(tokens(p["text"])) for p in source]
    average_length = sum(sum(doc.values()) for doc in documents) / len(documents)
    scores = []
    for document in documents:
        score = 0.0
        for term in set(tokens(query)):
            frequency = document[term]
            if frequency:
                df = sum(term in doc for doc in documents)
                idf = math.log(1 + (len(documents) - df + 0.5) / (df + 0.5))
                denominator = frequency + k1 * (1 - b + b * sum(document.values()) / average_length)
                score += idf * frequency * (k1 + 1) / denominator
        scores.append(score)
    return scores


class BM25SearchTests(unittest.TestCase):
    def test_matches_independent_formula_including_empty_paragraphs(self):
        source = [paragraph("a.txt", 1, "Ruby ruby the emerald x"),
                  paragraph("b.txt", 2, "emerald sapphire sapphire 22"),
                  paragraph("c.txt", 3, "ruby diamond"),
                  paragraph("d.txt", 4, "the and ..."),
                  paragraph("e.txt", 5, "")]
        for k1, b in [(1.2, 0.75), (0.4, 0), (2.0, 1)]:
            with self.subTest(k1=k1, b=b):
                expected = dict(zip([p["id"] for p in source], oracle_scores(source, "RUBY emerald ruby", k1=k1, b=b)))
                engine = BM25Search(source, k1=k1, b=b)
                results = engine.search("RUBY emerald ruby")
                self.assertEqual([p["id"] for p in results],
                                 [p["id"] for p in sorted(source, key=lambda p: -expected[p["id"]]) if expected[p["id"]] > 0])
                for result in results:
                    self.assertIsInstance(result["score"], float)
                    self.assertAlmostEqual(result["score"], expected[result["id"]])
                filtered = engine.search("ruby emerald", filename="b.txt")
                self.assertAlmostEqual(filtered[0]["score"], expected["b.txt:2"])

    def test_length_normalization_favors_shorter_paragraph(self):
        source = [paragraph("a.txt", 1, "ruby " + "emerald " * 30),
                  paragraph("b.txt", 1, "ruby")]
        self.assertEqual(BM25Search(source).search("ruby")[0]["filename"], "b.txt")
        tied = BM25Search(source, b=0).search("ruby")
        self.assertEqual(tied[0]["score"], tied[1]["score"])

    def test_term_frequency_saturates_and_rare_terms_have_larger_idf(self):
        source = [paragraph("a.txt", 1, "ruby"), paragraph("b.txt", 1, "ruby ruby"),
                  paragraph("c.txt", 1, "ruby ruby ruby ruby emerald")]
        scores = {p["filename"]: p["score"] for p in BM25Search(source, b=0).search("ruby")}
        self.assertGreater(scores["b.txt"], scores["a.txt"])
        self.assertLess((scores["c.txt"] - scores["b.txt"]) / 2,
                        scores["b.txt"] - scores["a.txt"])
        engine = BM25Search(source, b=0)
        self.assertGreater(engine.search("emerald")[0]["score"], scores["a.txt"])

    def test_query_terms_are_distinct(self):
        engine = BM25Search([paragraph("a.txt", 1, "ruby emerald"), paragraph("b.txt", 1, "emerald")])
        self.assertEqual(engine.search("ruby emerald"), engine.search("ruby ruby emerald ruby"))

    def test_top_five_and_all_tie_breakers(self):
        source = [paragraph("b.txt", 1, "ruby")]
        source += [paragraph("a.txt", line, "ruby") for line in range(7, 1, -1)]
        source += [paragraph("a.txt", 1, "ruby", end=3), paragraph("a.txt", 1, "ruby", end=2)]
        results = BM25Search(source).search("ruby")
        self.assertEqual([(p["filename"], p["line_start"], p["line_end"]) for p in results],
                         [("a.txt", 1, 2), ("a.txt", 1, 3), ("a.txt", 2, 2), ("a.txt", 3, 3), ("a.txt", 4, 4)])

    def test_filter_applies_before_limit(self):
        source = [paragraph("a.txt", line, "ruby") for line in range(1, 9)]
        source.append(paragraph("b.txt", 1, "ruby emerald"))
        results = BM25Search(source).search("ruby", filename="b.txt")
        self.assertEqual([p["filename"] for p in results], ["b.txt"])

    def test_threshold_is_inclusive_and_positive_scores_can_exceed_one(self):
        source = [paragraph("a.txt", 1, "ruby emerald sapphire diamond"),
                  paragraph("b.txt", 1, "quartz"), paragraph("c.txt", 1, "jade")]
        query = "ruby emerald sapphire diamond"
        score = BM25Search(source).search(query)[0]["score"]
        self.assertGreater(score, 1)
        self.assertEqual(len(BM25Search(source, min_score=score).search(query)), 1)
        self.assertEqual(BM25Search(source, min_score=math.nextafter(score, math.inf)).search(query), [])
        self.assertEqual(BM25Search(source, min_score=0).search(query)[0]["filename"], "a.txt")

    def test_metadata_copies_and_index_do_not_mutate_inputs(self):
        source = [paragraph("a.txt", 4, "ruby emerald")]
        before = copy.deepcopy(source)
        engine = BM25Search(source)
        result = engine.search("ruby")[0]
        self.assertEqual(source, before)
        self.assertIsNot(result, source[0])
        self.assertEqual({key: result[key] for key in before[0]}, before[0])
        result["title"] = "Changed result"
        source[0]["text"] = "sapphire"
        source.append(paragraph("b.txt", 1, "ruby"))
        self.assertEqual(engine.search("ruby")[0]["title"], "Synthetic title")
        self.assertEqual(engine.search("ruby")[0]["text"], "ruby emerald")
        self.assertEqual(engine.search("sapphire"), [])

    def test_fit_once_sparse_precomputation_and_query_reuse(self):
        original = CountVectorizer.fit_transform
        with patch.object(CountVectorizer, "fit_transform", autospec=True, side_effect=original) as fit:
            engine = BM25Search([paragraph("a.txt", 1, "ruby emerald"), paragraph("b.txt", 1, "sapphire")])
            weights = engine._matrix.copy()
            self.assertTrue(issparse(engine._matrix))
            for query in ["ruby", "emerald", "sapphire"]:
                engine.search(query)
                engine.search(query, filename="a.txt")
            self.assertEqual((engine._matrix != weights).nnz, 0)
        self.assertEqual(fit.call_count, 1)

    def test_empty_queries_stopwords_punctuation_and_oov(self):
        engine = BM25Search([paragraph("a.txt", 1, "ruby emerald")])
        for query in ["", " \t\n", "...!*", "the and is", "x", "sapphire"]:
            with self.subTest(query=query):
                self.assertEqual(engine.search(query), [])

    def test_empty_corpus_and_empty_vocabulary(self):
        for source in [[], [paragraph("a.txt", 1, "the and ...")], [paragraph("a.txt", 1, "")]]:
            with self.subTest(source=source):
                self.assertEqual(BM25Search(source).search("ruby"), [])

    def test_unknown_filename_raises_even_without_query_or_vocabulary(self):
        for source in [[], [paragraph("a.txt", 1, "the and")]]:
            with self.assertRaisesRegex(ValueError, "^Obra desconhecida: unknown.txt$"):
                BM25Search(source).search("", filename="unknown.txt")

    def test_invalid_numeric_parameters(self):
        for name, invalid in [("min_score", [-0.1, None]), ("k1", [0, -1]), ("b", [-0.1, 1.1])]:
            for value in invalid + [math.nan, math.inf, -math.inf, "0.5", True, False, {}]:
                with self.subTest(name=name, value=value), self.assertRaisesRegex(ValueError, name):
                    BM25Search([], **{name: value})
        for b in [0, 1]:
            BM25Search([], b=b, k1=0.001, min_score=100)

    def test_extreme_finite_k1_produces_finite_scores(self):
        source = [paragraph("a.txt", 1, "ruby ruby"), paragraph("b.txt", 1, "emerald")]
        for k1 in [sys.float_info.max, sys.float_info.min]:
            with self.subTest(k1=k1):
                result = BM25Search(source, k1=k1).search("ruby")[0]
                self.assertTrue(math.isfinite(result["score"]))
                self.assertGreater(result["score"], 0)

    def test_cli_metadata_score_and_empty_query(self):
        source = [paragraph("a.txt", 4, "ruby emerald", end=8)]
        for query, expected in [("ruby", "score BM25"), ("", "Nenhuma correspondência BM25")]:
            args = ["bm25", "--query", query, "--raw-dir", "synthetic", "--book", "a.txt", "--min-score", "0"]
            with self.subTest(query=query), patch("sys.argv", args):
                with patch("sherlock_search.bm25.prepare_corpus", return_value=(source, {})) as prepare:
                    buffer = io.StringIO()
                    with redirect_stdout(buffer):
                        main()
                    prepare.assert_called_once_with(Path("synthetic"))
                    self.assertIn(expected, buffer.getvalue())
                    self.assertNotIn("ruby emerald", buffer.getvalue())
                    if query:
                        self.assertIn("a.txt:4", buffer.getvalue())
                        self.assertIn("linhas 4-8", buffer.getvalue())
                        self.assertIn("Synthetic title", buffer.getvalue())

    def test_cli_errors_are_argparse_errors(self):
        cases = [(["--query", "ruby", "--min-score", "nan"], None, "min_score"),
                 (["--query", "ruby", "--book", "unknown.txt"], None, "Obra desconhecida"),
                 (["--query", "ruby"], OSError("synthetic read failure"), "synthetic read failure"),
                 ([], None, "--query")]
        for arguments, error, expected in cases:
            with self.subTest(arguments=arguments), patch("sys.argv", ["bm25", *arguments]):
                with patch("sherlock_search.bm25.prepare_corpus", return_value=([paragraph("a.txt", 1, "ruby")], {}), side_effect=error):
                    buffer = io.StringIO()
                    with redirect_stderr(buffer), self.assertRaises(SystemExit) as raised:
                        main()
                    self.assertEqual(raised.exception.code, 2)
                    self.assertIn(expected, buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
