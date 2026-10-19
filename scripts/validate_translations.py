#!/usr/bin/env python3
"""Validate the structure of the Unraid Traditional Chinese language pack.

Run from the repository root: python3 scripts/validate_translations.py
Only the right-hand side of KEY=translation may be localized.
"""
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent

TRANSLATION_FILES = [
    "translations.txt", "main.txt", "dashboard.txt", "shares.txt",
    "settings.txt", "docker.txt", "vms.txt", "tools.txt",
    "users.txt", "plugins.txt", "javascript.txt", "scripts.txt",
    "outgoingproxy.txt", "helptext.txt",
    "Community Apps/apps.txt", "Community Apps/ca_settings.txt",
    "Community Apps/javascript.ca.txt",
    "Dynamix System Stats/statsettings.txt",
    "Dynamix System Temp/tempsettings.txt",
    "CA Auto Update/autoupdateapps.txt",
    "CA Config File Edit/configedit.txt",
    "Recycle Bin/recyclebin.txt",
]

# Keep these technical names/symbols in English via the normal fallback.
ALLOWED_EMPTY = {
    "translations.txt": {"Docker", "Connect", "Rx", "Tx", "of"},
    "main.txt": {
        "raid0", "raid1", "raid10", "raid1c3", "raid1c4",
        "raid5", "raid6", "raidz", "raidz2", "raidz3",
        "Rx", "Tx", "W", "zfs",
    },
    "dashboard.txt": {"RX", "TX", "W", "ZFS"},
    "docker.txt": {"Tailscale"},
    "settings.txt": {
        "CRAM-MD5", "ipvlan", "macvlan", "NFSv3", "NFSv4", "NTP",
        "overlay2", "PTP", "raidz1", "TCP", "UDP", "UDPv4", "UDPv6",
        "Unraid Connect", "Wi-Fi", "zfs",
    },
}

# Some runtime UI components supply substitutions only in the translated
# template (the English lookup key does not contain those placeholders).
ALLOWED_DYNAMIC_FORMAT = {
    ("translations.txt", "You will no longer have access to this server using this url"),
}

# Ordinal printf formats (%1$s) are equivalent to ordinary %s for
# signature checking. Preserve both the count and the conversion types.
PRINTF = re.compile(r"%(?:[1-9]\d*\$)?[-+ #0]*\d*(?:\.\d+)?([sdfu])")
BLOCK_BEGIN = re.compile(r":[A-Za-z0-9_-]+_(?:help|plug):")

def formats(text: str) -> Counter[str]:
    return Counter(m.group(1) for m in PRINTF.finditer(text))

def check_file(relative: str) -> tuple[list[str], int, int]:
    errors: list[str] = []
    path = ROOT / relative
    try:
        raw = path.read_bytes()
        body = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"{relative}: could not read valid UTF-8 ({exc})"], 0, 0

    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{relative}: UTF-8 BOM is not supported")
    if b"\r" in raw:
        errors.append(f"{relative}: expected Unix LF line endings")

    active_block = None
    keys = 0
    empty = 0
    seen_empty: set[str] = set()
    labels: dict[str, str] = {}

    for lineno, line in enumerate(body.splitlines(), 1):
        if BLOCK_BEGIN.fullmatch(line):
            if active_block:
                errors.append(f"{relative}:{lineno}: nested translation block")
            active_block = line
            continue
        if line == ":end":
            if not active_block:
                errors.append(f"{relative}:{lineno}: unexpected :end")
            active_block = None
            continue
        if active_block or not line.strip() or line.startswith((";", "#")):
            continue
        if "=" not in line:
            errors.append(f"{relative}:{lineno}: expected KEY=translation")
            continue

        key, translated = line.split("=", 1)
        if not key:
            errors.append(f"{relative}:{lineno}: empty lookup key")
            continue
        keys += 1
        labels[key] = translated

        if not translated.strip():
            empty += 1
            seen_empty.add(key)
            if key not in ALLOWED_EMPTY.get(relative, set()):
                errors.append(f"{relative}:{lineno}: untranslated UI label: {key!r}")
            continue

        if formats(key) != formats(translated):
            if (relative, key) not in ALLOWED_DYNAMIC_FORMAT:
                errors.append(
                    f"{relative}:{lineno}: placeholder mismatch "
                    f"{dict(formats(key))!r} -> {dict(formats(translated))!r}"
                )

    if active_block:
        errors.append(f"{relative}: unterminated translation block {active_block}")

    if relative == "translations.txt":
        for key, expected in {
            "prefix_SI": "K M G T P E Z Y",
            "prefix_IEC": "Ki Mi Gi Ti Pi Ei Zi Yi",
        }.items():
            if labels.get(key) != expected:
                errors.append(f"{relative}: unexpected {key} unit prefixes")

    return errors, keys, empty

def main() -> int:
    failures = []
    total_keys = total_empty = 0
    for relative in TRANSLATION_FILES:
        errors, keys, empty = check_file(relative)
        failures.extend(errors)
        total_keys += keys
        total_empty += empty
        print(f"{relative}: {keys} labels, {empty} intentionally untranslated")
    if failures:
        print("\nTranslation validation failed:", file=sys.stderr)
        for error in failures:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"\nPASS: {len(TRANSLATION_FILES)} files, "
          f"{total_keys} labels, {total_empty} approved fallbacks.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
