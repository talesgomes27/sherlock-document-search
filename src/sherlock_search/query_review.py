"""Validate query proposals and render local source references; never run retrieval."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from .corpus import prepare_corpus, read_manifest


def prepare_reviews(queries_dir: Path, paragraphs: list[dict], output_dir: Path) -> dict:
    sources = {p["id"]: p for p in paragraphs}
    seen_queries = set()
    rendered = {}
    summary = {}
    for split, prefix, count in [("development", "dev", 10), ("final", "final", 20)]:
        path = Path(queries_dir) / f"{split}.json"
        data = path.read_bytes()
        rows = json.loads(data)
        if not isinstance(rows, list) or len(rows) != count:
            raise ValueError(f"{split}: esperado um conjunto com {count} consultas.")
        parts = [
            f"# Revisão humana — {split}",
            "Propostas de rótulos, não resultados de busca. Confira a consulta e suas fontes.",
            "Informe no chat os IDs aprovados e as correções; ou edite review_status no JSON de origem.",
            "Este arquivo é gerado e pode ser sobrescrito. As consultas finais não devem orientar ajustes.",
        ]
        for number, row in enumerate(rows, 1):
            identifier = f"{prefix}-{number:02}"
            if not isinstance(row, dict) or row.get("id") != identifier:
                raise ValueError(f"{split}: ID esperado {identifier}.")
            query = row.get("query")
            if not isinstance(query, str) or not query.strip():
                raise ValueError(f"{identifier}: consulta vazia ou inválida.")
            normalized = " ".join(query.split()).casefold()
            if normalized in seen_queries:
                raise ValueError(f"{identifier}: consulta duplicada entre os conjuntos.")
            seen_queries.add(normalized)
            if (not isinstance(row.get("query_type"), str)
                    or row["query_type"] not in {"term", "phrase", "question"}):
                raise ValueError(f"{identifier}: tipo de consulta inválido.")
            if (not isinstance(row.get("review_status"), str)
                    or row["review_status"] not in {"pending", "approved", "needs_changes"}):
                raise ValueError(f"{identifier}: status de revisão inválido.")
            references = row.get("relevant_ids")
            answerable = row.get("answerable")
            if (type(answerable) is not bool or not isinstance(references, list)
                    or any(not isinstance(r, str) for r in references)
                    or len(references) != len(set(references)) or bool(references) != answerable):
                raise ValueError(f"{identifier}: rótulo e referências incompatíveis.")
            if any(reference not in sources for reference in references):
                raise ValueError(f"{identifier}: referência inexistente no corpus verificado.")
            rationale = row.get("rationale")
            if not isinstance(rationale, str) or not rationale.strip():
                raise ValueError(f"{identifier}: justificativa ausente.")
            parts.extend([
                f"## {identifier}", f"**Consulta:** {query}",
                f"**Tipo:** {row['query_type']} · **Status:** {row['review_status']}",
                f"**Proposta:** {'com resposta' if answerable else 'sem resposta'}",
                f"**Justificativa a conferir:** {rationale}",
            ])
            for reference in references:
                paragraph = sources[reference]
                parts.extend([f"**Fonte:** {paragraph['title']} · `{reference}`", f"> {paragraph['text']}"])
            if not references:
                parts.append("Sem trecho proposto. A ausência de resposta exige revisão humana; palavras em comum não bastam.")
        if not 0 < sum(row["answerable"] for row in rows) < count:
            raise ValueError(f"{split}: inclua consultas com resposta e sem resposta.")
        summary[split] = {
            "file": path.name, "sha256": hashlib.sha256(data).hexdigest(), "queries": count,
            "answerable": sum(row["answerable"] for row in rows),
            "unanswerable": sum(not row["answerable"] for row in rows),
            "approved": sum(row["review_status"] == "approved" for row in rows),
            "needs_changes": sum(row["review_status"] == "needs_changes" for row in rows),
            "query_types": dict(Counter(row["query_type"] for row in rows)),
        }
        rendered[split] = "\n\n".join(parts) + "\n"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for split, markdown in rendered.items():
        (output_dir / f"{split}.md").write_text(markdown, encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepara fontes para revisão humana, sem executar busca.")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--queries-dir", type=Path, default=Path("evaluation"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/review"))
    args = parser.parse_args()
    try:
        paragraphs, _ = prepare_corpus(args.raw_dir)
        summary = prepare_reviews(args.queries_dir, paragraphs, args.output_dir)
        manifest = {
            "source_files": {f["filename"]: f["sha256"] for f in read_manifest()["files"]},
            "splits": summary,
        }
        (args.queries_dir / "split_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    for split, details in summary.items():
        print(f"{split}: {details['queries']} propostas; {details['approved']} aprovadas pelo revisor.")
    print(f"Fontes para revisão em {args.output_dir}. Nenhuma busca ou métrica foi executada.")


if __name__ == "__main__":
    main()
