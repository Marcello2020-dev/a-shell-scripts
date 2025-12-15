#!/usr/bin/env python3
import hashlib
from pathlib import Path

def read_expected(hash_path: Path) -> str:
    try:
        txt = hash_path.read_text(encoding="utf-8", errors="ignore").strip()
    except FileNotFoundError:
        return ""
    if not txt:
        return ""
    return txt.split()[0].lower()

ok = bad = miss = 0

for p in sorted(Path(".").glob("*.pdf")):
    hf_txt = p.with_suffix(".sha256.txt")
    hf_plain = p.with_suffix(".sha256")
    hf = hf_txt if hf_txt.exists() else (hf_plain if hf_plain.exists() else None)
    if hf is None:
        print(f"FEHLT HASH: {p.name}")
        miss += 1
        continue

    exp = read_expected(hf)
    if not exp:
        print(f"LEERE HASHDATEI: {hf.name} (zu {p.name})")
        bad += 1
        continue

    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk  in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    got = h.hexdigest().lower()

    if got == exp:
        ok += 1
    else:
        print(f"MISMATCH: {p.name}")
        print(f"  EXPECTED ({hf.name}): {exp}")
        print(f"  GOT                : {got}")
        bad += 1

print(f"OK={ok} MISMATCH={bad} FEHLT_HASH={miss}")
