#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional

CHUNK_SIZE = 1024 * 1024  # 1 MiB


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def read_expected(hashfile: Path) -> str:
    lines = hashfile.read_text(encoding="utf-8", errors="replace").splitlines()
    return (lines[0].strip() if lines else "")


def pdf_for_hashfile(hashfile: Path) -> Optional[Path]:
    # "<base>.sha256.txt" -> "<base>.pdf" oder "<base>.PDF"
    name = hashfile.name
    if not name.endswith(".sha256.txt"):
        return None
    base = name[:-len(".sha256.txt")]
    p1 = Path(base + ".pdf")
    if p1.exists():
        return p1
    p2 = Path(base + ".PDF")
    if p2.exists():
        return p2
    return None


def hashfile_for_pdf(pdf: Path) -> Path:
    # make_hashes macht: "<pdf-ohne-suffix>.sha256.txt"
    base = pdf.with_suffix("").name
    return Path(base + ".sha256.txt")


def main() -> int:
    here = Path.cwd()

    now = datetime.now()
    now_human = now.strftime("%Y-%m-%d %H:%M:%S")
    ts_filename = now.strftime("%Y-%m-%d_%H-%M-%S")

    out_name = f"VERIFY_SHA256_{ts_filename}.md"
    out_path = here / out_name

    hashfiles = sorted(here.glob("*.sha256.txt"), key=lambda p: p.name.lower())
    pdfs = sorted(
        [p for p in list(here.glob("*.pdf")) + list(here.glob("*.PDF")) if p.is_file()],
        key=lambda p: p.name.lower(),
    )

    ok = 0
    fail = 0
    missing_pdf = 0
    missing_hash = 0

    lines: list[str] = []
    lines.append("# Verify SHA-256 Report\n\n")
    lines.append(f"**Ausgeführt am:** {now_human}  \n")
    lines.append(f"**Ordner:** `{here.resolve()}`\n\n")

    # Tabelle 1: Hash-Dateien -> Prüfung
    lines.append("## Prüfungen (Hash-Datei → PDF)\n\n")
    lines.append("| Status | PDF | Hash-Datei | Expected SHA-256 | Actual SHA-256 |\n")
    lines.append("|---|---|---|---|---|\n")

    if not hashfiles:
        lines.append("| MISSING_HASHFILES | — | — | — | — |\n")
    else:
        for hf in hashfiles:
            expected = read_expected(hf)
            pdf = pdf_for_hashfile(hf)

            if pdf is None or not pdf.exists():
                lines.append(f"| MISSING_PDF | — | `{hf.name}` | `{expected}` | — |\n")
                missing_pdf += 1
                continue

            actual = sha256_file(pdf)

            if expected and actual.lower() == expected.lower():
                lines.append(f"| OK | `{pdf.name}` | `{hf.name}` | `{expected}` | `{actual}` |\n")
                ok += 1
            else:
                lines.append(f"| FAIL | `{pdf.name}` | `{hf.name}` | `{expected}` | `{actual}` |\n")
                fail += 1

    # Tabelle 2: PDFs ohne Hash-Datei
    lines.append("\n## PDFs ohne Hash-Datei\n\n")
    lines.append("| Status | PDF | Erwartete Hash-Datei |\n")
    lines.append("|---|---|---|\n")

    if not pdfs:
        lines.append("| NO_PDFS | — | — |\n")
    else:
        for pdf in pdfs:
            hf = hashfile_for_pdf(pdf)
            if not hf.exists():
                lines.append(f"| MISSING_HASH | `{pdf.name}` | `{hf.name}` |\n")
                missing_hash += 1

        if missing_hash == 0:
            lines.append("| OK | _Alle PDFs haben eine Hash-Datei_ | — |\n")

    # Summary
    lines.append("\n## Summary\n\n")
    lines.append(f"- OK: **{ok}**\n")
    lines.append(f"- FAIL: **{fail}**\n")
    lines.append(f"- MISSING_PDF: **{missing_pdf}**\n")
    lines.append(f"- MISSING_HASH: **{missing_hash}**\n")

    out_path.write_text("".join(lines), encoding="utf-8")
    print(f"OK: wrote {out_name}")

    return 0 if (fail == 0 and missing_pdf == 0 and missing_hash == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())