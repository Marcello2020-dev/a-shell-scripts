#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from datetime import datetime

SCRIPTS = {
    "make": "make_hashes.py",
    "verify": "verify_hashes.py",
    "list": "list_pdfs_report.py",
}

def run(script_path: Path) -> int:
    cmd = [sys.executable, "-u", str(script_path)]
    p = subprocess.run(cmd)
    return int(p.returncode)

def main() -> int:
    here = Path.cwd()
    repo = Path.home() / "Documents" / "bin" / "a-shell-scripts.git"

    print(f"CWD: {here.resolve()}")
    print(f"Repo: {repo.resolve()}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Existenzcheck
    for key, fn in SCRIPTS.items():
        p = repo / fn
        if not p.exists():
            print(f"ERROR: missing {key} script: {p}")
            return 2

    # Reihenfolge: make -> verify -> list
    for key in ("make", "verify", "list"):
        p = repo / SCRIPTS[key]
        print(f"== RUN {key.upper()} == {p.name}")
        rc = run(p)
        print(f"== EXIT {key.upper()} == {rc}\n")
        if rc != 0:
            print("Stopped because a step returned non-zero.")
            return rc

    print("DONE.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())