#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from datetime import datetime

def fmt_ts(ts: float | None) -> str:
    if ts is None:
        return "—"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

def get_created_ts(p: Path) -> float | None:
    st = p.stat()
    # iOS/macOS: st_birthtime ist oft vorhanden; sonst None
    bt = getattr(st, "st_birthtime", None)
    try:
        return float(bt) if bt is not None else None
    except Exception:
        return None

def main() -> None:
    here = Path(".")
    pdfs = sorted(
        [p for p in here.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"],
        key=lambda p: p.name.lower(),
    )

    now = datetime.now()
    now_human = now.strftime("%Y-%m-%d %H:%M:%S")
    ts_filename = now.strftime("%Y-%m-%d_%H-%M-%S")  # dateisystemfreundlich (ohne :)

    out_name = f"PDF_LIST_{ts_filename}.md"
    out_path = here / out_name

    lines: list[str] = []
    lines.append(f"# PDF-Report\n\n")
    lines.append(f"**Ausgeführt am:** {now_human}  \n")
    lines.append(f"**Ordner:** `{here.resolve()}`\n\n")

    lines.append("## Dateien\n\n")
    lines.append("| PDF | Größe (Bytes) | Erstellt | Geändert |\n")
    lines.append("|---|---:|---|---|\n")

    if pdfs:
        for p in pdfs:
            st = p.stat()
            created = get_created_ts(p)
            modified = float(st.st_mtime)
            lines.append(
                f"| `{p.name}` | {st.st_size} | {fmt_ts(created)} | {fmt_ts(modified)} |\n"
            )
    else:
        lines.append("| _Keine PDFs gefunden_ |  |  |  |\n")

    out_path.write_text("".join(lines), encoding="utf-8")
    print(f"OK: wrote {out_name}")

if __name__ == "__main__":
    main()