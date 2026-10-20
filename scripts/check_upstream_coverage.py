#!/usr/bin/env python3
"""Compare every translation lookup key and help section against upstream en_US.

Usage: python3 scripts/check_upstream_coverage.py /path/to/lang-en_US
The upstream git reference is pinned in .github/workflows/validate-translations.yml.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent


def translation_files(root: Path) -> dict[str, Path]:
    return {
        str(p.relative_to(root)): p
        for p in root.rglob("*.txt")
        if p.name != "LICENSE.txt" and ".git" not in p.parts
    }


def parse(path: Path) -> tuple[set[str], set[str]]:
    keys: set[str] = set()
    blocks: set[str] = set()
    active: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(":") and line.endswith(":") and line != ":end":
            # Unraid translation help sections, not arbitrary colon content.
            if line.endswith(("_help:", "_plug:")):
                active = line
                blocks.add(line)
                continue
        if line == ":end":
            active = None
            continue
        if active or not line.strip() or line.startswith((";", "#")):
            continue
        if "=" in line:
            key, _ = line.split("=", 1)
            if key:
                keys.add(key)
    return keys, blocks


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check_upstream_coverage.py UPSTREAM_LANG_EN_US_DIR")
        return 2
    upstream = Path(sys.argv[1]).resolve()
    if not upstream.is_dir():
        print(f"Upstream source directory unavailable: {upstream}")
        return 2

    en_files = translation_files(upstream)
    tw_files = translation_files(ROOT)
    missing_files = sorted(en_files.keys() - tw_files.keys())
    errors: list[str] = [f"Missing translation file: {x}" for x in missing_files]
    total_keys = matched_keys = 0
    total_blocks = matched_blocks = 0
    for rel, en_path in sorted(en_files.items()):
        source_keys, source_blocks = parse(en_path)
        total_keys += len(source_keys)
        total_blocks += len(source_blocks)
        if rel not in tw_files:
            continue
        tw_keys, tw_blocks = parse(tw_files[rel])
        matched_keys += len(source_keys & tw_keys)
        matched_blocks += len(source_blocks & tw_blocks)
        missing_keys = sorted(source_keys - tw_keys)
        missing_blocks = sorted(source_blocks - tw_blocks)
        errors.extend(f"{rel}: missing exact English key {key!r}" for key in missing_keys)
        errors.extend(f"{rel}: missing help block {tag}" for tag in missing_blocks)
        print(f"{rel}: {len(source_keys & tw_keys)}/{len(source_keys)} keys, "
              f"{len(source_blocks & tw_blocks)}/{len(source_blocks)} help sections")

    print(f"\nTOTAL: {len(en_files) - len(missing_files)}/{len(en_files)} files, "
          f"{matched_keys}/{total_keys} exact keys, "
          f"{matched_blocks}/{total_blocks} help sections")
    if errors:
        print("\nCoverage check failed:")
        for error in errors:
            print("  -", error)
        return 1
    print("PASS: all upstream translation files, keys and help sections are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
