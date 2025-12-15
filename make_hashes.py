#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_hashes.py — Generate SHA-256 checksum files for all PDFs in the CURRENT folder.

Output:
- For each PDF: <name>.sha256.txt  (one line: hex digest)
- README_SHA256.md                 (bilingual overview table)

Run it INSIDE the folder that contains the PDFs.
"""

import hashlib
from pathlib import Path
from datetime import datetime

CHUNK_SIZE = 1024 * 1024  # 1 MiB
README_NAME = "README_SHA256.md"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def fmt_bytes(n: int) -> str:
    return str(n)


def fmt_mtime(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def main() -> None:
    here = Path.cwd()

    # Robust PDF detection (case-insensitive)
    pdfs = sorted(
        [p for p in here.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"],
        key=lambda p: p.name.casefold(),
    )

    rows = []
    expected_hash_files = []

    for p in pdfs:
        digest = sha256_file(p)
        out = p.with_suffix(".sha256.txt")
        out.write_text(digest + "\n", encoding="utf-8")
        expected_hash_files.append(out)

        st = p.stat()
        rows.append((p.name, digest, out.name, st.st_size, fmt_mtime(st.st_mtime)))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    folder = str(here.resolve())

    # Build README
    lines = []
    lines.append("# SHA-256 Checksums (PDF)\n\n")
    lines.append(f"Generated: **{now}**  \n")
    lines.append(f"Folder: `{folder}`\n\n")

    lines.append("## Deutsch\n\n")
    lines.append(
        "Dieses Dokument wurde automatisch erzeugt. Es listet alle **PDF-Dateien im aktuellen Ordner** "
        "auf und enthält deren **SHA-256 Prüfsummen**.\n\n"
    )
    lines.append("### Dateien\n\n")
    if rows:
        lines.append("| PDF | SHA-256 | Hash-Datei | Größe (Bytes) | Geändert |\n")
        lines.append("|---|---|---|---:|---|\n")
        for name, digest, hashfile, size, mtime in rows:
            lines.append(f"| `{name}` | `{digest}` | `{hashfile}` | {size} | {mtime} |\n")
    else:
        lines.append("_Keine PDFs (`*.pdf`) im aktuellen Ordner gefunden._\n")

    lines.append("\n### Verifikation\n\n")
    lines.append("Im selben Ordner prüfen:\n\n")
    lines.append("```sh\n")
    lines.append('python3 "$HOME/Documents/bin/a-shell-scripts.git/verify_hashes.py"\n')
    lines.append("```\n\n")

    lines.append("## English\n\n")
    lines.append(
        "This file was generated automatically. It lists all **PDF files in the current folder** "
        "and their **SHA-256 checksums**.\n\n"
    )
    lines.append("### Files\n\n")
    if rows:
        lines.append("| PDF | SHA-256 | Hash file | Size (bytes) | Modified |\n")
        lines.append("|---|---|---|---:|---|\n")
        for name, digest, hashfile, size, mtime in rows:
            lines.append(f"| `{name}` | `{digest}` | `{hashfile}` | {size} | {mtime} |\n")
    else:
        lines.append("_No PDFs (`*.pdf`) found in the current folder._\n")

    lines.append("\n### Verification\n\n")
    lines.append("Verify in the same folder:\n\n")
    lines.append("```sh\n")
    lines.append('python3 "$HOME/Documents/bin/a-shell-scripts.git/verify_hashes.py"\n')
    lines.append("```\n")

    readme_path = here / README_NAME
    readme_path.write_text("".join(lines), encoding="utf-8")

    # --- Built-in “did we actually write files?” verification ---
    missing = []
    written = []

    for hf in expected_hash_files:
        if hf.exists():
            st = hf.stat()
            written.append((hf.name, st.st_size, fmt_mtime(st.st_mtime)))
        else:
            missing.append(hf.name)

    if readme_path.exists():
        st = readme_path.stat()
        written.append((readme_path.name, st.st_size, fmt_mtime(st.st_mtime)))
    else:
        missing.append(readme_path.name)

    print(f"CWD: {here}")
    print(f"PDFs found: {len(pdfs)}")
    print(f"OK: {len(expected_hash_files)} expected .sha256.txt + {README_NAME}")

    if written:
        print("\nWritten files:")
        for name, size, mtime in sorted(written, key=lambda x: x[0].casefold()):
            print(f"  {name}   {fmt_bytes(size)} bytes   {mtime}")

    if missing:
        print("\nERROR: Missing output files:")
        for name in missing:
            print(f"  {name}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()