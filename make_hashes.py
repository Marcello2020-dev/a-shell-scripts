#!/usr/bin/env python3
import hashlib
from pathlib import Path


ROOT = Path(".")
for p in ROOT.rglob("*.pdf"):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    out = p.with_suffix(".sha256.txt")  # Datei.pdf -> Datei.sha256.txt
    out.write_text(h.hexdigest() + "\n", encoding="utf-8")

print("OK")
