#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

# Welche MD-Reports sollen gelöscht werden?
MD_PREFIXES = (
    "PDF_LIST_",
    "SHA256_LIST_",
    "VERIFY_SHA256_",
)
MD_EXACT = {
    "README_SHA256.md",  # falls du das noch nutzt
}

def main() -> int:
    here = Path.cwd()

    sha_files = sorted([p for p in here.glob("*.sha256.txt") if p.is_file()], key=lambda p: p.name.lower())
    md_files = []
    for p in here.glob("*.md"):
        if not p.is_file():
            continue
        if p.name in MD_EXACT or any(p.name.startswith(pref) for pref in MD_PREFIXES):
            md_files.append(p)
    md_files = sorted(md_files, key=lambda p: p.name.lower())

    targets = sha_files + md_files

    print(f"CWD: {here.resolve()}")
    print(f"Found {len(sha_files)} sha256 files and {len(md_files)} md report files.")
    if not targets:
        print("Nothing to delete.")
        return 0

    print("\nWill delete:")
    for p in targets:
        print(f"  {p.name}")

    ans = input("\nDelete these files? [y/N] ").strip().lower()
    if ans != "y":
        print("Aborted.")
        return 1

    deleted = 0
    for p in targets:
        try:
            p.unlink()
            deleted += 1
        except Exception as e:
            print(f"ERROR deleting {p.name}: {e}")

    print(f"OK: deleted {deleted} file(s).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())