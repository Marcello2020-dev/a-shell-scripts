#!/usr/bin/env python3
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


def main() -> None:
    # Wichtig: im *aktuellen Ordner* arbeiten (da, wo du via pickFolder gelandet bist)
    here = Path.cwd()

    pdfs = sorted(
        [p for p in list(here.glob("*.pdf")) + list(here.glob("*.PDF")) if p.is_file()],
        key=lambda p: p.name.lower(),
    )

    rows = []
    for p in pdfs:
        digest = sha256_file(p)

        # pro PDF: file.pdf -> file.sha256.txt
        out = p.with_suffix(".sha256.txt")
        out.write_text(digest + "\n", encoding="utf-8")

        st = p.stat()
        size = st.st_size
        mtime = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        rows.append((p.name, digest, out.name, size, mtime))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    folder = str(here)

    lines = []
    lines.append("# SHA-256 Checksums (PDF)\n\n")
    lines.append(f"Generated: **{now}**  \n")
    lines.append(f"Folder: `{folder}`\n\n")

    # Deutsch
    lines.append("## Deutsch\n\n")
    lines.append(
        "Dieses Dokument wurde automatisch erzeugt. Es listet alle **PDF-Dateien im aktuellen Ordner** auf "
        "und enthält deren **SHA-256 Prüfsummen**.\n\n"
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

    # English
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

    Path(README_NAME).write_text("".join(lines), encoding="utf-8")
    print(f"OK: {len(rows)} PDFs → {len(rows)} .sha256.txt files + {README_NAME}")


if __name__ == "__main__":
    main()