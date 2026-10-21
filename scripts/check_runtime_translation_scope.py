#!/usr/bin/env python3
"""Audit translations against the *runtime source* and loading scope.

Upstream lang-en_US key coverage alone does not guarantee localized UI:
Unraid's Translations.php loads global translations.txt and then locale files
according to the request URI. Nchan device streams and plugin AJAX requests
can therefore miss strings only in main.txt or plugin-specific files.

Usage:
  python3 scripts/check_runtime_translation_scope.py WEBGUI_DIR UNASSIGNED_DEVICES_DIR

Source references are pinned by the GitHub Actions workflow.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent

# Static PHP translation calls and Unraid's inline _(word)_ markup.
QUOTED_PHP = re.compile(r"""\b_\(\s*(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)")\s*\)""")
INLINE = re.compile(r"_\((.+?)\)_")
HELP_BEGIN = re.compile(r":[A-Za-z0-9_-]+_(?:help|plug):")
PUNCTUATION = '?{}|&~![]()/:*^."\'\\'

# Endpoint contexts: the page on /Main can load main.txt;
# independent /sub/devices and /plugins/unassigned.devices/... requests
# must have translations globally available.
SOURCES = (
    ("core Main UI", "webgui",
     "emhttp/plugins/dynamix/ArrayOperation.page", ("translations.txt", "main.txt")),
    ("core device stream", "webgui",
     "emhttp/plugins/dynamix/nchan/device_list", ("translations.txt",)),
    ("Unassigned Devices Main panel", "ud",
     "source/unassigned.devices/usr/local/emhttp/plugins/unassigned.devices/UnassignedDevices.page",
     ("translations.txt",)),
    ("Unassigned Devices AJAX", "ud",
     "source/unassigned.devices/usr/local/emhttp/plugins/unassigned.devices/include/UnassignedDevices.php",
     ("translations.txt",)),
)

# Explicitly guard user-reported failures, regardless of parser improvements.
REQUIRED_GLOBAL = (
    "will take the array offline",
    "Internal Boot",
    "No internal boot setup detected Launch %s to configure one",
    "ONLINE",
    "Unassigned Disk Devices",
    "Historical Unassigned Devices",
    "Serial Number Mount Point",
    "SMB Shares",
    "NFS Shares",
    "ISO File Shares",
    "Share Type",
    "Source",
    "Mount Point",
    "Add Remote SMB",
    "NFS Share",
    "Add ISO File Share",
    "Add Root Share",
    "No Remote SMB",
    "NFS or ISO File Shares configured",
)


def lookup_key(text: str) -> str:
    """Mirror Translations.php _(): trim, remove punctuation, collapse spaces."""
    text = text.strip()
    text = re.sub(r"<.+?/?>", "", text)
    text = text.replace("&amp;", "")
    text = text.translate(str.maketrans("", "", PUNCTUATION))
    return re.sub(r"  +", " ", text).strip()


def labels_from_file(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    inside_help = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if HELP_BEGIN.fullmatch(line):
            inside_help = True
            continue
        if line == ":end":
            inside_help = False
            continue
        if inside_help or not line or line.startswith((";", "#")) or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key and value.strip():
            result[key] = value.strip()
    return result


def source_keys(path: Path) -> set[str]:
    src = path.read_text(encoding="utf-8")
    result: set[str] = set()
    strings = [a or b for a, b in QUOTED_PHP.findall(src)]
    strings.extend(INLINE.findall(src))
    for raw in strings:
        if any(token in raw for token in ("$", "<?", "\n", "\r")):
            continue
        key = lookup_key(raw)
        if key and len(key) <= 200:
            result.add(key)
    return result


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: check_runtime_translation_scope.py WEBGUI_DIR UD_DIR")
        return 2
    source_roots = {"webgui": Path(sys.argv[1]), "ud": Path(sys.argv[2])}
    dicts = {p: labels_from_file(ROOT / p) for p in
             ("translations.txt", "main.txt",
              "Unassigned Devices/unassigneddevices.txt",
              "Unassigned Devices/unassigneddevicessettings.txt",
              "Dynamix S3 Sleep/sleepsettings.txt")}
    errors: list[str] = []
    global_keys = dicts["translations.txt"]

    # The plugin label files may be available on some requests and absent on
    # others: keeping their keys in the global catalog is the fallback.
    for plugin_file in (
        "Unassigned Devices/unassigneddevices.txt",
        "Unassigned Devices/unassigneddevicessettings.txt",
        "Dynamix S3 Sleep/sleepsettings.txt",
    ):
        labels = dicts[plugin_file]
        missing = sorted(set(labels) - set(global_keys))
        errors.extend(f"{plugin_file}: not accessible globally: {k}" for k in missing)
        print(f"{plugin_file}: {len(labels)-len(missing)}/{len(labels)} global fallback keys")

    for label, root_name, relative, available_files in SOURCES:
        filepath = source_roots[root_name] / relative
        if not filepath.is_file():
            errors.append(f"Missing pinned runtime source: {filepath}")
            continue
        extracted = source_keys(filepath)
        available = set().union(*(dicts[name] for name in available_files))
        missing = sorted(extracted - available)
        errors.extend(f"{label}: untranslated runtime key {k!r}" for k in missing)
        print(f"{label}: {len(extracted)-len(missing)}/{len(extracted)} "
              f"static runtime lookup keys available")

    for key in REQUIRED_GLOBAL:
        if not global_keys.get(key):
            errors.append(f"Required Main/UD runtime key unavailable globally: {key}")

    expected = "未設定遠端 SMB/NFS 或 ISO 檔案共享。"
    rendered = (global_keys.get("No Remote SMB", "") + "/" +
                global_keys.get("NFS or ISO File Shares configured", "") + "。")
    if rendered != expected:
        errors.append(f"Remote share notice assembled incorrectly: {rendered!r}")
    if global_keys.get("Source") != "來源":
        errors.append("The Share Type table column Source must be 來源")

    if errors:
        print("\nRuntime translation coverage FAILED:", file=sys.stderr)
        for error in errors:
            print("  - " + error, file=sys.stderr)
        return 1

    print("\nPASS: runtime Main/UD translations are available in their loading contexts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
