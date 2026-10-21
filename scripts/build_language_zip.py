#!/usr/bin/env python3
"""Build a Unraid-importable zh_TW.zip from translation source files.

Run from repository root: python3 scripts/build_language_zip.py
The ZIP preserves plugin subfolder structure, without repository metadata.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

# Helpers.php in Unraid WebGUI uses explode(' ', ' '.prefix) to select units.
EXPECTED_PREFIXES = {
    'prefix_SI': 'K M G T P E Z Y',
    'prefix_IEC': 'Ki Mi Gi Ti Pi Ei Zi Yi',
}


def validate_prefixes(data: str) -> None:
    rows = [line for line in data.splitlines() if line.startswith(tuple(key + '=' for key in EXPECTED_PREFIXES))]
    for key, expected in EXPECTED_PREFIXES.items():
        matches = [row.split('=', 1)[1] for row in rows if row.startswith(key + '=')]
        if matches != [expected]:
            raise RuntimeError(f'Unexpected {key} in packaged language: {matches!r}; expected {expected!r}')
        prefix_parts = matches[0].split(' ')
        assert len(prefix_parts) == 8 and all(prefix_parts)


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
    # Verify the actual installable ZIP, not only the working-tree file.
    with ZipFile(OUT) as z:
        validate_prefixes(z.read('translations.txt').decode('utf-8'))
    print(f"Verified SI/IEC units in packaged {OUT.relative_to(ROOT)}")
    print(f"Created {OUT.relative_to(ROOT)} with {len(files)} translation files")


if __name__ == "__main__":
    main()
