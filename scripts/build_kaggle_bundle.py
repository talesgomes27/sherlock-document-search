"""Refresh the notebook's deterministic code bundle without including source books."""

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import zipfile


def build_bundle(root):
    snapshot = json.loads((root / "evaluation/m3_freeze.json").read_text())
    files = {}
    for name, expected in snapshot["file_sha256"].items():
        content = (root / name).read_bytes()
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError(f"Frozen input changed: {name}")
        files[name] = content
    for name in ("evaluation/m3_freeze.json", "src/sherlock_search/final_evaluation.py"):
        files[name] = (root / name).read_bytes()
    files["README.md"] = b"# Sherlock Holmes document retrieval\n\nCode and metadata for this notebook analysis.\n"
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)
    return output.getvalue()


def refresh(root, check=False):
    path = root / "notebooks/sherlock_document_search.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    cells = [cell for cell in notebook["cells"] if "embedded-code" in cell["metadata"].get("tags", [])]
    if len(cells) != 1:
        raise ValueError("Expected one embedded-code cell.")
    cell = cells[0]
    source = "".join(cell["source"])
    payload = build_bundle(root)
    header = f'BUNDLE_B64 = "{base64.b64encode(payload).decode()}"\nBUNDLE_SHA256 = "{hashlib.sha256(payload).hexdigest()}"\n'
    source = header + "# END EMBEDDED PAYLOAD\n" + source.split("# END EMBEDDED PAYLOAD\n", 1)[1]
    if check:
        if source != "".join(cell["source"]):
            raise ValueError("Notebook code bundle is out of date.")
    else:
        cell["source"] = source
        for item in notebook["cells"]:
            if item["cell_type"] == "code":
                item["execution_count"], item["outputs"] = None, []
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Notebook bundle verified: {len(payload)} bytes; no source TXT included.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    refresh(Path(__file__).resolve().parents[1], check=args.check)
