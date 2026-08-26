#!/usr/bin/env python3
"""Build a deterministic Terminal Python data package from Chaquopy stdlib."""

import argparse
import hashlib
import json
import stat
import zipfile
from pathlib import Path


WRAPPER = b"""#!/system/bin/sh
if [ -z "$PREFIX" ] || [ -z "$TERMINAL_NATIVE_LIB_DIR" ]; then
    echo "python: Terminal native runtime environment is unavailable" >&2
    exit 126
fi
export PYTHONHOME="$PREFIX"
export PYTHONPATH="$PREFIX/lib/python313.zip:$TERMINAL_NATIVE_LIB_DIR${PYTHONPATH:+:$PYTHONPATH}"
export LD_LIBRARY_PATH="$TERMINAL_NATIVE_LIB_DIR${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec "$TERMINAL_NATIVE_LIB_DIR/libterminal_python.so" "$@"
"""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add_file(archive: zipfile.ZipFile, path: str, data: bytes, executable: bool) -> None:
    info = zipfile.ZipInfo(path, (1980, 1, 1, 0, 0, 0))
    mode = 0o755 if executable else 0o644
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stdlib", type=Path, help="Chaquopy target-*-stdlib-pyc.zip")
    parser.add_argument("output", type=Path)
    parser.add_argument("--version", default="3.13.0")
    parser.add_argument("--abi", required=True, choices=("arm64-v8a", "x86_64"))
    parser.add_argument("--min-api", type=int, default=29)
    args = parser.parse_args()

    stdlib = args.stdlib.read_bytes()
    if not zipfile.is_zipfile(args.stdlib):
        raise SystemExit(f"not a ZIP archive: {args.stdlib}")
    files = [
        ("usr/bin/python", WRAPPER, True),
        ("usr/bin/python3", WRAPPER, True),
        ("usr/lib/python313.zip", stdlib, False),
    ]
    manifest = {
        "schemaVersion": 1,
        "id": "python",
        "version": args.version,
        "abi": args.abi,
        "minApi": args.min_api,
        "dependencies": [],
        "files": [
            {"path": path, "size": len(data), "sha256": digest(data), "executable": executable}
            for path, data, executable in files
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", allowZip64=True) as archive:
        info = zipfile.ZipInfo("terminal-package.json", (1980, 1, 1, 0, 0, 0))
        info.external_attr = (stat.S_IFREG | 0o644) << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n")
        for path, data, executable in files:
            add_file(archive, path, data, executable)
    print(f"{args.output} {args.output.stat().st_size} {digest(args.output.read_bytes())}")


if __name__ == "__main__":
    main()
