"""Run with python -m sherlock_search --help."""

import argparse
import json
from pathlib import Path
from zipfile import BadZipFile

from .corpus import download_corpus, prepare_corpus


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepara o corpus Sherlock com referências às linhas originais.")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--download", action="store_true", help="Baixa e verifica o snapshot em uma pasta nova.")
    args = parser.parse_args()
    if args.raw_dir.resolve() == args.output_dir.resolve():
        parser.error("As pastas de origem e saída devem ser diferentes.")
    try:
        if args.download:
            download_corpus(args.raw_dir)
        paragraphs, report = prepare_corpus(args.raw_dir)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        with (args.output_dir / "paragraphs.jsonl").open("w", encoding="utf-8") as output:
            for paragraph in paragraphs:
                output.write(json.dumps(paragraph, ensure_ascii=False) + "\n")
        (args.output_dir / "quality.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError, BadZipFile) as error:
        parser.error(str(error))
    totals = report["totals"]
    print(f"{totals['files']} arquivos verificados; {totals['paragraphs']} parágrafos em {args.output_dir}.")


if __name__ == "__main__":
    main()
