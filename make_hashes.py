#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path
from datetime import datetime

CHUNK_SIZE = 1024 * 1024  # 1 MiB


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def fmt_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def main() -> None:
    here = Path.cwd()

    now = datetime.now()
    now_human = now.strftime("%Y-%m-%d %H:%M:%S")
    ts_filename = now.strftime("%Y-%m-%d_%H-%M-%S")

    out_md_name = f"SHA256_LIST_{ts_filename}.md"
    out_md_path = here / out_md_name

    # PDFs im aktuellen Ordner (case-insensitive .pdf / .PDF)
    pdfs = sorted(
        [p for p in here.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"],
        key=lambda p: p.name.lower(),
    )

    rows = []

    for p in pdfs:
        digest = sha256_file(p)

        # Hash-Datei neben die PDF: name.sha256.txt
        out_hash = p.with_suffix(".sha256.txt")
        out_hash.write_text(digest + "\n", encoding="utf-8")

        st = p.stat()
        rows.append(
            {
                "pdf": p.name,
                "size": st.st_size,
                "modified": fmt_ts(st.st_mtime),
                "hashfile": out_hash.name,
                "sha256": digest,
            }
        )

    # Markdown-Report im gleichen Stil wie die anderen Reports
    lines: list[str] = []
    lines.append("# SHA-256 Report\n\n")
    lines.append(f"**Ausgeführt am:** {now_human}  \n")
    lines.append(f"**Ordner:** `{here.resolve()}`\n\n")

    lines.append("## Dateien\n\n")
    lines.append("| PDF | Größe (Bytes) | Geändert | Hash-Datei | SHA-256 |\n")
    lines.append("|---|---:|---|---|---|\n")

    if rows:
        for r in rows:
            lines.append(
                f"| `{r['pdf']}` | {r['size']} | {r['modified']} | `{r['hashfile']}` | `{r['sha256']}` |\n"
            )
    else:
        lines.append("| _Keine PDFs gefunden_ |  |  |  |  |\n")

    lines.append("\n## Nutzung\n\n")
    lines.append("Im selben Ordner prüfen:\n\n")
    lines.append("```sh\n")
    lines.append('python3 "$HOME/Documents/bin/a-shell-scripts.git/verify_hashes.py"\n')
    lines.append("```\n")

    out_md_path.write_text("".join(lines), encoding="utf-8")
    print(f"OK: {len(rows)} PDFs → {len(rows)} .sha256.txt + {out_md_name}")


if __name__ == "__main__":
    main()