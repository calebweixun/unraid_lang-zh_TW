#!/usr/bin/env python3
"""Build a Unraid-importable zh_TW.zip from translation source files.

Run from repository root: python3 scripts/build_language_zip.py
The ZIP preserves plugin subfolder structure, without repository metadata.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "zh_TW.zip"


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if path.suffix != ".txt" or path.name == "LICENSE.txt":
        return False
    if any(part.startswith(".") for part in relative.parts):
        return False
    if "dist" in relative.parts:
        return False
    return True


def main() -> None:
    files = sorted(path for path in ROOT.rglob("*.txt") if included(path))
    if not files:
        raise RuntimeError("No translation files found")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUT, "w", compression=ZIP_DEFLATED) as z:
        for path in files:
            z.write(path, path.relative_to(ROOT).as_posix())
    print(f"Created {OUT.relative_to(ROOT)} with {len(files)} translation files")


if __name__ == "__main__":
    main()
