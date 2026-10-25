"""Calibrate abstention using only the ten approved development queries."""

import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform

from .corpus import prepare_corpus
from .search import literal_search
from .tfidf import TfidfSearch


THRESHOLDS = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)


def load_development(directory: Path) -> list[dict]:
    directory = Path(directory)
    manifest = json.loads((directory / "split_manifest.json").read_text(encoding="utf-8"))
    try:
        expected = manifest["splits"]["development"]
        expected_hash = expected["sha256"]
        approved = expected["approved"]
    except (KeyError, TypeError) as error:
        raise ValueError("Manifesto de desenvolvimento inválido.") from error
    data = (directory / "development.json").read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_hash:
        raise ValueError("SHA-256 de desenvolvimento divergente do snapshot aprovado.")
    queries = json.loads(data)
    if (not isinstance(queries, list) or len(queries) != 10
            or any(not isinstance(q, dict) for q in queries)
            or [q.get("id") for q in queries] != [f"dev-{i:02}" for i in range(1, 11)]
            or approved != 10
            or any(q.get("review_status") != "approved" for q in queries)):
        raise ValueError("São necessárias as dez consultas de desenvolvimento aprovadas.")
    for query in queries:
        references = query.get("relevant_ids")
        if (not isinstance(query.get("query"), str) or not query["query"].strip()
                or type(query.get("answerable")) is not bool
                or not isinstance(references, list)
                or any(not isinstance(reference, str) for reference in references)
                or len(references) != len(set(references))
                or bool(references) != query["answerable"]):
            raise ValueError(f"Consulta ou rótulo inválido: {query['id']}")
    return queries


def verify_freeze(root: Path) -> dict:
    root = Path(root).resolve()
    snapshot = json.loads((root / "evaluation/m3_freeze.json").read_text(encoding="utf-8"))
    if (not isinstance(snapshot, dict) or not isinstance(snapshot.get("file_sha256"), dict)
            or not snapshot["file_sha256"]):
        raise ValueError("Manifesto congelado inválido ou vazio.")
    for relative, expected_hash in snapshot["file_sha256"].items():
        if not isinstance(relative, str):
            raise ValueError("Manifesto congelado contém caminho inválido.")
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Manifesto congelado contém caminho fora do projeto.")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
            raise ValueError(f"Arquivo congelado divergente: {relative}")
    return snapshot


def summarize(queries: list[dict], predictions: dict) -> dict:
    positive = [q for q in queries if q["answerable"]]
    negative = [q for q in queries if not q["answerable"]]
    if not positive or not negative:
        raise ValueError("A calibração exige as duas classes de consultas.")
    hits = sum(bool(set(q["relevant_ids"]) & {p["id"] for p in predictions[q["id"]]}) for q in positive)
    false_positives = sum(bool(predictions[q["id"]]) for q in negative)
    hit_rate = hits / len(positive)
    false_rate = false_positives / len(negative)
    return {
        "positive_queries": len(positive), "positive_hits": hits, "known_hit_at_5": hit_rate,
        "negative_queries": len(negative), "false_positive_queries": false_positives,
        "false_positive_rate": false_rate,
        "balanced_utility": (hit_rate + 1 - false_rate) / 2,
    }


def choose_threshold(candidates: list[dict]) -> float:
    baseline_hits = next(row["positive_hits"] for row in candidates if row["min_score"] == 0)
    eligible = [row for row in candidates if row["positive_hits"] >= baseline_hits]
    return min(eligible, key=lambda row: (row["false_positive_rate"], row["min_score"]))["min_score"]


def compare_development(paragraphs: list[dict], queries: list[dict]) -> dict:
    source_ids = {p["id"] for p in paragraphs}
    if any(reference not in source_ids for q in queries for reference in q["relevant_ids"]):
        raise ValueError("Referência de desenvolvimento ausente no corpus.")
    index = TfidfSearch(paragraphs, min_score=0)
    raw = {q["id"]: index.search(q["query"]) for q in queries}
    literal = {q["id"]: literal_search(paragraphs, q["query"]) for q in queries}
    candidates = []
    for threshold in THRESHOLDS:
        predictions = {key: [p for p in results if p["score"] >= threshold] for key, results in raw.items()}
        candidates.append({"min_score": threshold, **summarize(queries, predictions)})
    selected = choose_threshold(candidates)
    predictions = {key: [p for p in results if p["score"] >= selected] for key, results in raw.items()}
    details = []
    for q in queries:
        details.append({
            "id": q["id"], "answerable": q["answerable"], "known_relevant_ids": q["relevant_ids"],
            "literal": [{"id": p["id"], "score": p["score"]} for p in literal[q["id"]]],
            "tfidf": [{"id": p["id"], "score": p["score"]} for p in predictions[q["id"]]],
        })
    return {
        "split": "development", "query_count": len(queries),
        "selection_rule": "Preserve unthresholded positive_hits; minimize false_positive_rate among eligible thresholds; ties prefer lower threshold.",
        "vectorizer": "TfidfVectorizer(stop_words='english'); other scikit-learn defaults.",
        "threshold_grid": candidates, "selected_min_score": selected,
        "literal": summarize(queries, literal), "tfidf": summarize(queries, predictions),
        "results": details,
        "versions": {"python": platform.python_version(), **{name: version(name) for name in ["scikit-learn", "numpy", "scipy"]}},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara métodos usando somente desenvolvimento.")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--queries-dir", type=Path, default=Path("evaluation"))
    parser.add_argument("--output", type=Path, default=Path("reports/m3_development.json"))
    parser.add_argument("--check-freeze", action="store_true", help="Confere hashes do snapshot, sem executar consultas.")
    args = parser.parse_args()
    if args.check_freeze:
        try:
            snapshot = verify_freeze(Path.cwd())
        except (OSError, ValueError, KeyError) as error:
            parser.error(str(error))
        print(f"Snapshot M3 conferido: {len(snapshot['file_sha256'])} arquivos. Nenhuma consulta executada.")
        return
    output = args.output.resolve()
    for directory in [args.raw_dir.resolve(), args.queries_dir.resolve()]:
        if output.is_relative_to(directory):
            parser.error("A saída não pode sobrescrever ou ficar dentro das pastas de insumos.")
    try:
        queries = load_development(args.queries_dir)
        paragraphs, _ = prepare_corpus(args.raw_dir)
        report = compare_development(paragraphs, queries)
        report["development_sha256"] = hashlib.sha256((args.queries_dir / "development.json").read_bytes()).hexdigest()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))
    print(f"10 consultas de desenvolvimento; limiar selecionado: {report['selected_min_score']:.1f}.")
    for method in ["literal", "tfidf"]:
        values = report[method]
        print(f"{method}: {values['positive_hits']}/{values['positive_queries']} positivas com trecho conhecido no top 5; "
              f"{values['false_positive_queries']}/{values['negative_queries']} negativas com retorno indevido.")
    print("Nenhuma consulta final foi carregada ou executada.")


if __name__ == "__main__":
    main()
