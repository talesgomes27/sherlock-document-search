"""Literal retrieval; no learned parameters or evaluation labels are used."""

import re


def literal_search(paragraphs: list[dict], query: str, *, filename: str | None = None) -> list[dict]:
    """Return up to five paragraphs, ranked by non-overlapping occurrences."""
    if filename is not None and filename not in {p["filename"] for p in paragraphs}:
        raise ValueError(f"Obra desconhecida: {filename}")
    query = " ".join(query.split()).casefold()
    if not any(char.isalnum() for char in query):
        return []
    expression = r"\s+".join(re.escape(part) for part in query.split())
    pattern = re.compile(r"(?<!\w)" + expression + r"(?!\w)")
    results = []
    for paragraph in paragraphs:
        if filename is not None and paragraph["filename"] != filename:
            continue
        occurrences = sum(1 for _ in pattern.finditer(paragraph["text"].casefold()))
        if occurrences:
            results.append({**paragraph, "score": occurrences})
    results.sort(key=lambda p: (-p["score"], p["filename"], p["line_start"], p["line_end"]))
    return results[:5]
