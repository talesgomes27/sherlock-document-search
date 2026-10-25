"""Evaluate the approved final split once with the frozen M3 retrieval methods."""

import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform

from .corpus import prepare_corpus
from .development import summarize, verify_freeze
from .search import literal_search
from .tfidf import TfidfSearch


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_versions() -> dict:
    return {"python": platform.python_version(),
            **{name: version(name) for name in ("scikit-learn", "numpy", "scipy")}}


def verify_sources(root: Path, snapshot: dict) -> None:
    """Ensure --root describes the package actually executing the experiment."""
    package = Path(__file__).resolve().parent
    for relative, expected in snapshot["file_sha256"].items():
        path = Path(relative)
        if path.parts[:2] == ("src", "sherlock_search"):
            if sha256(package / path.relative_to("src/sherlock_search")) != expected:
                raise ValueError(f"Arquivo importado divergente do congelado: {relative}")
    if sha256(package / "final_evaluation.py") != sha256(root / "src/sherlock_search/final_evaluation.py"):
        raise ValueError("Avaliador importado divergente do projeto informado.")


def load_final(root: Path) -> list[dict]:
    queries = json.loads((root / "evaluation/final.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "evaluation/split_manifest.json").read_text(encoding="utf-8"))
    metadata = manifest["splits"]["final"]
    counts = {"queries": 20, "answerable": 16, "unanswerable": 4, "approved": 20, "needs_changes": 0}
    if any(type(metadata.get(key)) is not int or metadata[key] != count for key, count in counts.items()):
        raise ValueError("Metadados do split final divergentes de M2.")
    if (not isinstance(queries, list) or len(queries) != 20
            or any(not isinstance(query, dict) for query in queries)
            or [query.get("id") for query in queries] != [f"final-{i:02}" for i in range(1, 21)]
            or any(query.get("review_status") != "approved" for query in queries)):
        raise ValueError("São necessárias as vinte consultas finais aprovadas.")
    for query in queries:
        references = query.get("relevant_ids")
        if (not isinstance(query.get("query"), str) or not query["query"].strip()
                or type(query.get("answerable")) is not bool
                or not isinstance(references, list)
                or any(not isinstance(reference, str) or not reference for reference in references)
                or len(references) != len(set(references))
                or bool(references) != query["answerable"]):
            raise ValueError(f"Consulta ou rótulo final inválido: {query['id']}")
    if sum(query["answerable"] for query in queries) != metadata["answerable"]:
        raise ValueError("Rótulos finais divergentes das 16 positivas e 4 negativas de M2.")
    return queries


def evaluate_final(root: Path, raw_dir: Path) -> dict:
    root, raw_dir = Path(root).resolve(), Path(raw_dir).resolve()
    snapshot = verify_freeze(root)
    freeze_hash = sha256(root / "evaluation/m3_freeze.json")
    versions = runtime_versions()
    if versions["python"] != "3.11.17" or versions != snapshot["runtime_versions"]:
        raise ValueError("Versões de runtime divergentes do snapshot M3 (Python exato 3.11.17).")
    verify_sources(root, snapshot)
    evaluator_hash = sha256(Path(__file__).resolve())
    queries = load_final(root)
    paragraphs, corpus = prepare_corpus(raw_dir)
    source_ids = {paragraph["id"] for paragraph in paragraphs}
    if any(reference not in source_ids for query in queries for reference in query["relevant_ids"]):
        raise ValueError("Referência final ausente no corpus.")
    index = TfidfSearch(paragraphs)
    if index.min_score != snapshot["tfidf"]["min_score"]:
        raise ValueError("min_score divergente do snapshot M3.")
    literal = {query["id"]: literal_search(paragraphs, query["query"]) for query in queries}
    tfidf = {query["id"]: index.search(query["query"]) for query in queries}
    if verify_freeze(root) != snapshot or sha256(root / "evaluation/m3_freeze.json") != freeze_hash:
        raise ValueError("Manifesto congelado alterado durante a avaliação.")
    verify_sources(root, snapshot)
    if sha256(Path(__file__).resolve()) != evaluator_hash:
        raise ValueError("Avaliador alterado durante a avaliação.")
    if {path.name for path in raw_dir.glob("*.txt") if path.is_file()} != {source["filename"] for source in corpus["files"]}:
        raise ValueError("Inventário do corpus alterado durante a avaliação.")
    for source in corpus["files"]:
        if sha256(raw_dir / source["filename"]) != source["sha256"]:
            raise ValueError(f"Corpus alterado durante a avaliação: {source['filename']}")
    return {
        "split": "final", "query_count": len(queries),
        "vectorizer": snapshot["tfidf"]["vectorizer"], "selected_min_score": index.min_score,
        "literal": summarize(queries, literal), "tfidf": summarize(queries, tfidf),
        "results": [{"id": query["id"], "answerable": query["answerable"],
                     "known_relevant_ids": query["relevant_ids"],
                     **{method: [{"id": row["id"], "score": row["score"]} for row in results[query["id"]]]
                        for method, results in (("literal", literal), ("tfidf", tfidf))}}
                    for query in queries],
        "corpus": corpus, "versions": versions, "m3_freeze_sha256": freeze_hash,
        "evaluator_sha256": evaluator_hash,
    }


def validate_output(root: Path, raw_dir: Path, output: Path, snapshot: dict) -> None:
    protected = [root / relative for relative in snapshot["file_sha256"]]
    protected.extend([root / "evaluation/m3_freeze.json", root / "src/sherlock_search/final_evaluation.py"])
    if (output.is_relative_to(raw_dir) or output.is_relative_to(root / "data/raw")
            or output.is_relative_to(root / "evaluation")
            or any(output == path.resolve() or (output.exists() and path.exists() and output.samefile(path))
                   for path in protected)):
        raise ValueError("A saída não pode sobrescrever insumos ou arquivos congelados.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Avalia as vinte consultas finais sem novo ajuste.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, default=Path("reports/m4_final.json"))
    args = parser.parse_args()
    root = args.root.resolve()
    raw_dir = (root / args.raw_dir).resolve()
    output = (root / args.output).resolve()
    try:
        snapshot = verify_freeze(root)
        validate_output(root, raw_dir, output, snapshot)
        report = evaluate_final(root, raw_dir)
        validate_output(root, raw_dir, output, snapshot)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(f"20 consultas finais avaliadas; relatório: {output}")


if __name__ == "__main__":
    main()
