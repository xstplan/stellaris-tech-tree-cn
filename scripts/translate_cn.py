#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="One-command Chinese i18n generation for a Stellaris tech-tree version."
    )
    parser.add_argument(
        "--version",
        default="phoenix-4.0.10",
        help="Version directory name (default: phoenix-4.0.10).",
    )
    parser.add_argument(
        "--stellaris-dir",
        default=None,
        help="Optional Stellaris install directory. If omitted, auto-detect from Steam.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    build_script = repo_root / "scripts" / "build_phoenix_i18n.py"

    version_dir = repo_root / args.version
    if not version_dir.exists():
        print(f"ERROR: version directory not found: {version_dir}", file=sys.stderr)
        return 2

    out_path = version_dir / "i18n.zh-hans.json"
    cmd = [
        sys.executable,
        str(build_script),
        "--phoenix-dir",
        args.version,
        "--out",
        str(Path(args.version) / "i18n.zh-hans.json"),
    ]
    if args.stellaris_dir:
        cmd.extend(["--stellaris-dir", args.stellaris_dir])

    result = subprocess.run(cmd, cwd=repo_root)
    if result.returncode != 0:
        return result.returncode

    print(f"Done: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
