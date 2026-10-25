"""Synthetic fixtures are generated here; original books are never committed."""

import hashlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from sherlock_search.corpus import (
    count_words,
    download_corpus,
    prepare_corpus,
    read_manifest,
    source_lines,
    split_paragraphs,
)


class PreparationTests(unittest.TestCase):
    def test_word_count_excludes_unicode_numbers_and_keeps_internal_connectors(self):
        self.assertEqual(count_words("4½ per cent. ² Ⅳ ٣"), 2)
        self.assertEqual(count_words("Watson's two-line English 文"), 4)

    def test_line_endings_bom_and_unicode_separator(self):
        data = b"\xef\xbb\xbfFirst\r\nSecond\rThird\n"
        self.assertEqual(source_lines(data), ["First", "Second", "Third"])
        self.assertEqual(source_lines("A\u2028B\n".encode()), ["A\u2028B"])

    def test_paragraphs_preserve_source_lines_and_last_paragraph(self):
        lines = ["header", "", "  First line", "second line  ", "  ", "Last", "footer"]
        paragraphs = split_paragraphs(lines, "synthetic.txt", "Synthetic", 3, 6)
        self.assertEqual(
            [(p["line_start"], p["line_end"], p["text"]) for p in paragraphs],
            [(3, 4, "First line second line"), (6, 6, "Last")],
        )
        self.assertEqual(paragraphs[0]["id"], "synthetic.txt:3-4")
        self.assertEqual(paragraphs[0]["title"], "Synthetic")
        self.assertEqual(paragraphs[0]["filename"], "synthetic.txt")

    def test_invalid_source_range_is_rejected(self):
        for first, last in [(0, 1), (2, 1), (1, 3)]:
            with self.subTest(first=first, last=last), self.assertRaises(ValueError):
                split_paragraphs(["one", "two"], "synthetic.txt", "Synthetic", first, last)

    def test_missing_extra_and_changed_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = synthetic_manifest(b"header\n\nNarrative.\nfooter\n")
            with patch("sherlock_search.corpus.read_manifest", return_value=manifest):
                with self.assertRaisesRegex(ValueError, "inventário"):
                    prepare_corpus(root)
                path = root / "synthetic.txt"
                path.write_bytes(b"header\n\nNarrative.\nfooter\n")
                (root / "unexpected.txt").write_text("extra", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "inventário"):
                    prepare_corpus(root)
                (root / "unexpected.txt").unlink()
                path.write_bytes(b"header\n\nChanged!!!\nfooter\n")
                with self.assertRaisesRegex(ValueError, "SHA-256"):
                    prepare_corpus(root)

    def test_quality_counts_and_exclusion_of_editorial_material(self):
        content = b"header\n\nNarrative with two-line\nwords and Watson's letter.\nfooter\n"
        manifest = synthetic_manifest(content, first=3, last=4)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "synthetic.txt").write_bytes(content)
            with patch("sherlock_search.corpus.read_manifest", return_value=manifest):
                paragraphs, report = prepare_corpus(root)
        self.assertEqual(len(paragraphs), 1)
        self.assertEqual(report["totals"]["files"], 1)
        self.assertEqual(report["totals"]["paragraphs"], 1)
        self.assertEqual(report["files"][0]["source_words"], 9)
        self.assertEqual(report["files"][0]["retained_words"], 7)
        self.assertEqual(report["files"][0]["removed_words"], 2)
        self.assertNotIn("header", paragraphs[0]["text"])
        self.assertNotIn("footer", paragraphs[0]["text"])


def synthetic_manifest(content, first=3, last=3):
    return {
        "dataset_url": "https://example.invalid/synthetic-fixture",
        "archive_url": "https://example.invalid/synthetic-fixture.zip",
        "archive_sha256": "replaced by download tests",
        "archive_size_bytes": 0,
        "files": [{
            "filename": "synthetic.txt",
            "title": "Synthetic fixture",
            "size_bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "body_start_line": first,
            "body_end_line": last,
        }],
    }


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.content = b"header\n\nNarrative.\nfooter\n"
        self.manifest = synthetic_manifest(self.content)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("synthetic.txt", self.content)
        self.archive = buffer.getvalue()
        self.manifest["archive_sha256"] = hashlib.sha256(self.archive).hexdigest()
        self.manifest["archive_size_bytes"] = len(self.archive)

    def download(self, destination, content=None):
        response = io.BytesIO(self.archive if content is None else content)
        with patch("sherlock_search.corpus.read_manifest", return_value=self.manifest):
            with patch("sherlock_search.corpus.urlopen", return_value=response):
                download_corpus(destination)

    def test_verified_archive_download_and_existing_directory_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "raw"
            self.download(destination)
            self.assertEqual((destination / "synthetic.txt").read_bytes(), self.content)
            with self.assertRaises(FileExistsError):
                self.download(destination)
            self.assertEqual((destination / "synthetic.txt").read_bytes(), self.content)

    def test_changed_archive_leaves_no_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "raw"
            with self.assertRaisesRegex(ValueError, "ZIP"):
                self.download(destination, b"unexpected data")
            self.assertFalse(destination.exists())

    def test_unexpected_zip_member_is_not_extracted(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("../outside.txt", self.content)
        self.archive = buffer.getvalue()
        self.manifest["archive_sha256"] = hashlib.sha256(self.archive).hexdigest()
        self.manifest["archive_size_bytes"] = len(self.archive)
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "raw"
            with self.assertRaisesRegex(ValueError, "inventário"):
                self.download(destination)
            self.assertFalse(destination.exists())
            self.assertFalse((Path(directory) / "outside.txt").exists())


REAL_RAW_DIR = Path(os.environ.get("SHERLOCK_RAW_DIR", "data/raw"))


@unittest.skipUnless(REAL_RAW_DIR.is_dir(), "Download the corpus or set SHERLOCK_RAW_DIR for real-corpus checks")
class RealCorpusTests(unittest.TestCase):
    def test_nine_original_files_and_every_paragraph_round_trip(self):
        directory = REAL_RAW_DIR
        paragraphs, report = prepare_corpus(directory)
        self.assertEqual(len(report["files"]), 9)
        self.assertEqual(report["totals"]["size_bytes"], 4041127)
        self.assertGreater(len(paragraphs), 10000)
        originals = {
            f["filename"]: source_lines((directory / f["filename"]).read_bytes())
            for f in read_manifest()["files"]
        }
        self.assertEqual(len({p["id"] for p in paragraphs}), len(paragraphs))
        for p in paragraphs:
            lines = originals[p["filename"]][p["line_start"] - 1:p["line_end"]]
            self.assertEqual(p["text"], " ".join(line.strip() for line in lines))
        study = [p for p in paragraphs if p["filename"] == "a_study_in_scarlet.txt"]
        self.assertIn("Ipse domi", study[-1]["text"])
        self.assertEqual(study[-1]["line_end"], 4712)
        self.assertFalse(any(p["text"].strip() == "THE END" for p in paragraphs))


if __name__ == "__main__":
    unittest.main()
