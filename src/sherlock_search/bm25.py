"""In-memory BM25 retrieval; scores are unbounded relevance weights, not probabilities."""

import argparse
import math
from numbers import Real
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

from .corpus import prepare_corpus


class BM25Search:
    def __init__(self, paragraphs: list[dict], *, k1: float = 1.2,
                 b: float = 0.75, min_score: float = 0.0):
        for name, value in (("k1", k1), ("b", b), ("min_score", min_score)):
            if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
                raise ValueError(f"{name} deve ser um número finito")
        if k1 <= 0:
            raise ValueError("k1 deve ser maior que zero")
        if not 0 <= b <= 1:
            raise ValueError("b deve estar entre 0 e 1")
        if min_score < 0:
            raise ValueError("min_score deve ser maior ou igual a zero")
        k1 = float(k1)
        self.min_score = float(min_score)
        self._paragraphs = [dict(paragraph) for paragraph in paragraphs]
        self._filenames = {paragraph["filename"] for paragraph in self._paragraphs}
        self._vectorizer = CountVectorizer(stop_words="english")
        self._matrix = None
        if not self._paragraphs:
            return
        try:
            counts = self._vectorizer.fit_transform([p["text"] for p in self._paragraphs])
        except ValueError as error:
            if "empty vocabulary" not in str(error):
                raise
            return
        lengths = np.asarray(counts.sum(axis=1)).ravel()
        n = len(self._paragraphs)
        document_frequency = np.bincount(counts.indices, minlength=counts.shape[1])
        idf = np.log1p((n - document_frequency + 0.5) / (document_frequency + 0.5))
        normalization = 1 - b + b * lengths / lengths.mean()
        rows = np.repeat(np.arange(n), np.diff(counts.indptr))
        weights = counts.astype(float)
        # Divide by k1 + 1 first to avoid overflowing tf * (k1 + 1).
        weights.data /= weights.data / (k1 + 1) + (k1 / (k1 + 1)) * normalization[rows]
        weights.data *= idf[weights.indices]
        self._matrix = weights

    def search(self, query: str, *, filename: str | None = None) -> list[dict]:
        """Return at most five positive matches after filtering and thresholding."""
        if filename is not None and filename not in self._filenames:
            raise ValueError(f"Obra desconhecida: {filename}")
        if self._matrix is None:
            return []
        query_vector = self._vectorizer.transform([query])
        if query_vector.nnz == 0:
            return []
        scores = np.asarray(self._matrix[:, query_vector.indices].sum(axis=1)).ravel()
        results = [
            {**paragraph, "score": float(score)}
            for paragraph, score in zip(self._paragraphs, scores)
            if score > 0 and score >= self.min_score
            and (filename is None or paragraph["filename"] == filename)
        ]
        results.sort(key=lambda p: (-p["score"], p["filename"], p["line_start"], p["line_end"]))
        return results[:5]


def main() -> None:
    parser = argparse.ArgumentParser(description="Busca BM25 com referências às linhas originais.")
    parser.add_argument("--query", required=True, help="Consulta textual; termos repetidos contam uma vez.")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--book", help="Filtra pelo nome exato do arquivo TXT.")
    parser.add_argument("--min-score", type=float, default=0.0,
                        help="Score BM25 mínimo, não negativo; não é probabilidade.")
    args = parser.parse_args()
    try:
        paragraphs, _ = prepare_corpus(args.raw_dir)
        results = BM25Search(paragraphs, min_score=args.min_score).search(args.query, filename=args.book)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if not results:
        print("Nenhuma correspondência BM25 atende ao limiar.")
    for rank, paragraph in enumerate(results, 1):
        print(f"[{rank}] {paragraph['title']} | {paragraph['id']} | "
              f"linhas {paragraph['line_start']}-{paragraph['line_end']} | "
              f"score BM25: {paragraph['score']:.6f}")


if __name__ == "__main__":
    main()
