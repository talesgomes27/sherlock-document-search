"""Prepare paragraphs while preserving references to the original TXT lines."""

import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen
from zipfile import ZipFile


WORDS = re.compile(r"[^\W\d_]+(?:['’\-][^\W\d_]+)*")


def count_words(text: str) -> int:
    # Regex \d alone does not exclude Unicode fractions such as ½.
    without_numbers = "".join(" " if char.isnumeric() else char for char in text)
    return len(WORDS.findall(without_numbers))


def read_manifest() -> dict:
    return json.loads(Path(__file__).with_name("corpus_manifest.json").read_text(encoding="utf-8"))


def source_lines(data: bytes) -> list[str]:
    text = data.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    if text.endswith("\n"):
        lines.pop()
    return lines


def split_paragraphs(
    lines: list[str], filename: str, title: str, first_line: int, last_line: int
) -> list[dict]:
    """Use inclusive, one-based source line ranges; join wrapped lines with spaces."""
    if not 1 <= first_line <= last_line <= len(lines):
        raise ValueError(f"Intervalo de linhas inválido: {filename}:{first_line}-{last_line}")
    paragraphs = []
    block = []
    start = first_line
    for number in range(first_line, last_line + 2):
        line = lines[number - 1].strip() if number <= last_line else ""
        if line:
            if not block:
                start = number
            block.append(line)
        elif block:
            paragraphs.append({
                "id": f"{filename}:{start}-{number - 1}",
                "filename": filename,
                "title": title,
                "line_start": start,
                "line_end": number - 1,
                "text": " ".join(block),
            })
            block = []
    return paragraphs


def _verify_file(data: bytes, specification: dict) -> None:
    if (len(data) != specification["size_bytes"]
            or hashlib.sha256(data).hexdigest() != specification["sha256"]):
        raise ValueError(
            f"Tamanho ou SHA-256 divergente: {specification['filename']}. "
            "Confira a origem e revise o manifesto antes de aceitar outro snapshot."
        )


def download_corpus(raw_dir: Path) -> None:
    """Validate the complete ZIP before creating a new raw-data directory."""
    raw_dir = Path(raw_dir)
    if raw_dir.exists():
        raise FileExistsError(f"Pasta já existe: {raw_dir}. Reutilize-a sem --download.")
    manifest = read_manifest()
    request = Request(manifest["archive_url"], headers={"User-Agent": "sherlock-document-search/0.1"})
    with urlopen(request, timeout=60) as response:
        data = response.read(manifest["archive_size_bytes"] + 1)
    if (len(data) != manifest["archive_size_bytes"]
            or hashlib.sha256(data).hexdigest() != manifest["archive_sha256"]):
        raise ValueError("ZIP diferente do snapshot esperado; nenhum TXT foi gravado.")
    contents = {}
    with ZipFile(BytesIO(data)) as archive:
        names = [f["filename"] for f in manifest["files"]]
        if sorted(archive.namelist()) != sorted(names):
            raise ValueError("ZIP com inventário diferente do esperado; nenhum TXT foi gravado.")
        for specification in manifest["files"]:
            name = specification["filename"]
            if archive.getinfo(name).file_size != specification["size_bytes"]:
                raise ValueError(f"Tamanho descompactado inesperado: {name}")
            contents[name] = archive.read(name)
            _verify_file(contents[name], specification)
    raw_dir.mkdir(parents=True, exist_ok=False)
    for name, content in contents.items():
        (raw_dir / name).write_bytes(content)


def prepare_corpus(raw_dir: Path) -> tuple[list[dict], dict]:
    """Require the exact recorded snapshot, both locally and on Kaggle."""
    raw_dir = Path(raw_dir)
    manifest = read_manifest()
    expected = {f["filename"] for f in manifest["files"]}
    actual = {p.name for p in raw_dir.glob("*.txt") if p.is_file()}
    if actual != expected:
        raise ValueError(
            f"Divergência no inventário. Ausentes: {sorted(expected - actual)}; "
            f"inesperados: {sorted(actual - expected)}. Confira --raw-dir."
        )
    paragraphs = []
    statistics = []
    for specification in manifest["files"]:
        filename = specification["filename"]
        data = (raw_dir / filename).read_bytes()
        _verify_file(data, specification)
        lines = source_lines(data)
        # shortcut: recortes deste snapshot; revisar os limites ao aceitar outra versão.
        extracted = split_paragraphs(
            lines, filename, specification["title"],
            specification["body_start_line"], specification["body_end_line"],
        )
        if not extracted:
            raise ValueError(f"Nenhum parágrafo encontrado: {filename}")
        paragraphs.extend(extracted)
        source_words = count_words("\n".join(lines))
        retained_words = sum(count_words(p["text"]) for p in extracted)
        statistics.append({
            "filename": filename,
            "title": specification["title"],
            "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "source_lines": len(lines),
            "body_start_line": specification["body_start_line"],
            "body_end_line": specification["body_end_line"],
            "source_words": source_words,
            "retained_words": retained_words,
            "removed_words": source_words - retained_words,
            "paragraphs": len(extracted),
        })
    totals = {
        key: sum(f[key] for f in statistics)
        for key in ("size_bytes", "source_lines", "source_words", "retained_words", "removed_words", "paragraphs")
    }
    totals["files"] = len(statistics)
    report = {
        "dataset_url": manifest["dataset_url"],
        "word_count_rule": "Unicode letters with optional internal apostrophe or hyphen; numbers excluded.",
        "files": statistics,
        "totals": totals,
    }
    return paragraphs, report
