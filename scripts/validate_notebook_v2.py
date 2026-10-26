"""Execute the separate v2 notebook in a clean local kernel; this is not a Kaggle run."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import nbformat
from nbclient import NotebookClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--expected-report", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.is_relative_to(args.raw_dir.resolve()):
        parser.error("A validação não pode gravar dentro dos dados de origem.")
    output.mkdir(parents=True, exist_ok=False)
    work = output / "run"
    notebook = nbformat.read(args.notebook, as_version=4)
    nbformat.validate(notebook)
    source_cells = [cell.source for cell in notebook.cells]
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.outputs, cell.execution_count = [], None
    os.environ["SHERLOCK_NOTEBOOK_WORK_DIR"] = str(work)
    os.environ["SHERLOCK_RAW_DIR"] = str(args.raw_dir.resolve())
    os.environ["IPYTHONDIR"] = str(output / "ipython")
    os.environ["JUPYTER_RUNTIME_DIR"] = str(output / "jupyter-runtime")
    os.environ["JUPYTER_PATH"] = str(Path(sys.prefix) / "share/jupyter")
    subprocess.run([sys.executable, "-m", "ipykernel", "install", "--prefix", sys.prefix,
                    "--name", "sherlock-v2-validation", "--display-name", "Sherlock v2 local QA"],
                   check=True, text=True, capture_output=True)
    client = NotebookClient(notebook, timeout=900, kernel_name="sherlock-v2-validation",
                            resources={"metadata": {"path": str(output)}})
    executed = client.execute()
    assert [cell.source for cell in executed.cells] == source_cells, "Notebook source changed."
    code_cells = [cell for cell in executed.cells if cell.cell_type == "code"]
    assert [cell.execution_count for cell in code_cells] == list(range(1, len(code_cells) + 1))
    assert not any(item.output_type == "error" for cell in code_cells for item in cell.outputs)
    figures = sorted((work / "figures").glob("*"))
    assert [path.name for path in figures] == ["corpus_size.png", "corpus_size.svg", "final_comparison.png", "final_comparison.svg"]
    assert all(path.stat().st_size > 1000 for path in figures), "Missing or empty chart."
    image_count = sum("image/png" in item.get("data", {}) for cell in code_cells for item in cell.outputs)
    assert image_count == 2, "Expected two inline charts."
    report = work / "search_results.json"
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["split"] == "v2_final" and data["query_count"] == 24
    assert set(data["methods"]) == {"literal_v1", "tfidf_v1", "bm25"}
    assert report.read_bytes() == args.expected_report.read_bytes(), "Notebook and reference report differ."
    executed.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
    for cell in executed.cells:
        if "embedded-code-v2" in cell.metadata.get("tags", []):
            cell.metadata.setdefault("jupyter", {})["source_hidden"] = True
    artifact = output / "sherlock_document_search_v2.ipynb"
    nbformat.write(executed, artifact)
    evidence = {
        "environment": "local_clean_kernel_not_kaggle", "study": "v2", "code_cells_executed": len(code_cells),
        "cell_errors": 0, "inline_charts": image_count, "figure_files": [path.name for path in figures], "source_cells_unchanged": True, "report_byte_identical": True,
        "notebook_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        "final_report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
        "versions": json.loads(report.read_text(encoding="utf-8"))["versions"],
    }
    (output / "validation.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
