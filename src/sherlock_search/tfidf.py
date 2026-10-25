"""In-memory TF-IDF retrieval with cosine similarity scores, not probabilities."""

import json
import math
from numbers import Real
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TfidfSearch:
    def __init__(self, paragraphs: list[dict], *, min_score: float | None = None):
        if min_score is None:
            config_path = Path(__file__).with_name("tfidf_config.json")
            try:
                min_score = json.loads(config_path.read_text(encoding="utf-8"))["min_score"]
            except (OSError, ValueError, KeyError, TypeError) as error:
                raise ValueError(f"Configuração min_score inválida: {config_path}") from error
        if isinstance(min_score, bool) or not isinstance(min_score, Real) or not math.isfinite(min_score) or not 0 <= min_score <= 1:
            raise ValueError("min_score deve ser um número finito entre 0 e 1")
        self.min_score = float(min_score)
        self._paragraphs = [dict(paragraph) for paragraph in paragraphs]
        self._filenames = {paragraph["filename"] for paragraph in self._paragraphs}
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = None
        if self._paragraphs:
            try:
                self._matrix = self._vectorizer.fit_transform([p["text"] for p in self._paragraphs])
            except ValueError as error:
                if "empty vocabulary" not in str(error):
                    raise

    def search(self, query: str, *, filename: str | None = None) -> list[dict]:
        """Return at most five positive matches after filtering and thresholding."""
        if filename is not None and filename not in self._filenames:
            raise ValueError(f"Obra desconhecida: {filename}")
        if self._matrix is None:
            return []
        query_vector = self._vectorizer.transform([query])
        if query_vector.nnz == 0:
            return []
        scores = cosine_similarity(query_vector, self._matrix)[0]
        results = [
            {**paragraph, "score": float(score)}
            for paragraph, score in zip(self._paragraphs, scores)
            if score > 0 and score >= self.min_score
            and (filename is None or paragraph["filename"] == filename)
        ]
        results.sort(key=lambda p: (-p["score"], p["filename"], p["line_start"], p["line_end"]))
        return results[:5]
