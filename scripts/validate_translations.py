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


# Flag Simplified-only characters and known misleading translation phrases.
SIMPLIFIED_ONLY = re.compile(
    r"[这们吗为会过还从发经网软盘页图标简设选显断编务数归户开关识销结进读键诊络"
    r"贴购题动权试级导写应员没间顶声创观黄议资录壳处协议长隐细预内许继于扩稳谢]"
)
BAD_TERMS = re.compile(
    r"同位元檢查磁碟|同位元檢查檢查|奇偶校驗|CPU\s*討論串|虛擬機器器"
)
HAN = re.compile(r"[\u3400-\u9fff]")
ASCII_PROSE = re.compile(r"^[A-Za-z0-9 _.,!?;:()'/\-+&*]+$")
ALLOW_ENGLISH_VALUES = {"Numbers_array", "prefix_SI", "prefix_IEC",
                        "Active Directory", "httpIPport or httphostport"}

def check_localization_text(relative: str, lineno: int, value: str,
                            is_block: bool = False, key: str = "") -> list[str]:
    issues: list[str] = []
    if SIMPLIFIED_ONLY.search(value):
        issues.append(f"{relative}:{lineno}: likely Simplified Chinese in translation")
    if BAD_TERMS.search(value):
        issues.append(f"{relative}:{lineno}: deprecated or inaccurate terminology")
    if key in ALLOW_ENGLISH_VALUES:
        return issues

    candidate = value.strip()
    code_tick = chr(96)
    if is_block and (
        not candidate or candidate.startswith((";", "#", code_tick, "'tailscale"))
        or code_tick in candidate or candidate.startswith(("<?", "config/"))
        or re.match(r"^[+*]\s*\d", candidate) or ".pem" in candidate
    ):
        return issues

    if (len(candidate) >= 40 and not HAN.search(candidate)
            and ASCII_PROSE.fullmatch(candidate)):
        issues.append(f"{relative}:{lineno}: likely untranslated English sentence")
    return issues


# Guard the most visible Parity terms from accidental global replacements.
PARITY_EXPECTATIONS = {
    "translations.txt": {
        "Parity": "同位元校驗",
        "Parity-Check": "同位元校驗檢查",
        "Parity-Sync": "同位元校驗同步",
    },
    "dashboard.txt": {
        "Parity disk not present": "未偵測到校驗磁碟",
    },
    "settings.txt": {
        "Parity Check": "同位元校驗檢查",
    },
}


# Fail on regressions in particularly misleading or unsafe UI labels.
CRITICAL_UI_TRANSLATIONS = {
    "translations.txt": {
        "No errors reported": "沒有回報任何錯誤",
        "Device": "裝置",
    },
    "main.txt": {
        "Array Devices": "陣列裝置",
        "Unassigned Devices": "未指派裝置",
    },
    "settings.txt": {
        "Display world-wide-name in device ID":
            "在裝置識別碼中顯示全球唯一名稱（WWN）",
    },
}

# Safety-related help sections must retain their core warning or direction.
REQUIRED_HELP_MARKERS = {
    "info_file_system_help": ("格式化", "清除", "備份"),
    "info_btrfs_check_help": ("--readonly", "--repair", "危險"),
    "info_btrfs_scrub_help": ("資料校驗", "備援", "備份"),
    "docker_appdata_location_help": ("正斜線", "/config"),
    "mgmt_certificate_expiration_help": ("DNS", "保護"),
}

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
    block_text: dict[str, list[str]] = {}
    keys = 0
    empty = 0
    seen_empty: set[str] = set()
    labels: dict[str, str] = {}

    for lineno, line in enumerate(body.splitlines(), 1):
        if BLOCK_BEGIN.fullmatch(line):
            if active_block:
                errors.append(f"{relative}:{lineno}: nested translation block")
            active_block = line
            if relative == "helptext.txt":
                block_text[line.strip(":").removesuffix("_help").removesuffix("_plug")] = []
            continue
        if line == ":end":
            if not active_block:
                errors.append(f"{relative}:{lineno}: unexpected :end")
            active_block = None
            continue
        if active_block:
            if relative == "helptext.txt":
                block_text[active_block.strip(":").removesuffix("_help").removesuffix("_plug")].append(line)
            if not line.startswith((";", "#")):
                errors.extend(check_localization_text(relative, lineno, line, is_block=True))
            continue
        if not line.strip() or line.startswith((";", "#")):
            continue
        if "=" not in line:
            errors.append(f"{relative}:{lineno}: expected KEY=translation")
            continue

        key, translated = line.split("=", 1)
        if not key:
            errors.append(f"{relative}:{lineno}: empty lookup key")
            continue
        keys += 1
        if key in labels and labels[key] != translated:
            errors.append(f"{relative}:{lineno}: conflicting translation for {key!r}")
        labels[key] = translated

        if not translated.strip():
            empty += 1
            seen_empty.add(key)
            if key not in ALLOWED_EMPTY.get(relative, set()):
                errors.append(f"{relative}:{lineno}: untranslated UI label: {key!r}")
            continue

        errors.extend(check_localization_text(relative, lineno, translated, key=key))

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

    for key, expected in PARITY_EXPECTATIONS.get(relative, {}).items():
        if labels.get(key) != expected:
            errors.append(f"{relative}: expected {key!r} to be {expected!r}")

    for key, expected in CRITICAL_UI_TRANSLATIONS.get(relative, {}).items():
        if labels.get(key) != expected:
            errors.append(f"{relative}: critical label {key!r} must remain {expected!r}")

    if relative == "helptext.txt":
        for name, required_terms in REQUIRED_HELP_MARKERS.items():
            body = "\n".join(block_text.get(name, []))
            if not body:
                errors.append(f"{relative}: missing required help block {name!r}")
                continue
            for term in required_terms:
                if term not in body:
                    errors.append(
                        f"{relative}: required text {term!r} missing in {name!r}"
                    )

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
