# Author: Lead + agent | Task: automatic dataset root detection | PR: TBD
# Status: original implementation by this team
"""Find the dataset root automatically under /kaggle/input (the level that contains data/D1/defect).

Why this is needed:
    Kaggle's dataset mount paths differ between environments and over time (for example
    /kaggle/input/<slug>/  or  /kaggle/input/datasets/<owner>/<slug>/), so hardcoding them causes an
    immediate FileNotFoundError on some kernels. This module performs one search and supports both layouts.

Usage:
    python -m src.locate_data                     # print the path found, exit code 0/1
    python -m src.locate_data --diagnose          # print the structure of /kaggle/input when not found
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

MARKER = ("data", "D1", "defect")


def find_root(search_root: str = "/kaggle/input", max_depth: int = 5) -> str | None:
    base = Path(search_root)
    if not base.is_dir():
        return None
    base_depth = len(base.parts)
    for dirpath, dirnames, _ in os.walk(base):
        p = Path(dirpath)
        if (p / MARKER[0] / MARKER[1] / MARKER[2]).is_dir():
            return str(p)
        if len(p.parts) - base_depth >= max_depth:
            dirnames[:] = []
    return None


def diagnose(search_root: str = "/kaggle/input") -> None:
    base = Path(search_root)
    if not base.is_dir():
        print(f"[locate] {search_root} does not exist")
        return
    base_depth = len(base.parts)
    for dirpath, dirnames, filenames in os.walk(base):
        p = Path(dirpath)
        depth = len(p.parts) - base_depth
        if depth > 3:
            dirnames[:] = []
            continue
        print(f"[locate] {dirpath}  dirs={dirnames[:6]}  files={filenames[:3]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--search-root", default="/kaggle/input")
    ap.add_argument("--diagnose", action="store_true")
    ap.add_argument("--wait", type=int, default=0,
                    help="maximum number of seconds to wait (Kaggle mounts can be delayed by seconds to tens of seconds)")
    args = ap.parse_args()

    import time

    deadline = time.time() + max(args.wait, 0)
    attempt = 0
    while True:
        attempt += 1
        root = find_root(args.search_root)
        if root:
            print(root)  # print only the path so that $(...) can capture it in a shell
            return
        if time.time() >= deadline:
            break
        print(f"[locate] attempt {attempt} found nothing, retrying in 10s ...", file=sys.stderr)
        time.sleep(10)

    if args.diagnose:
        diagnose(args.search_root)
    print(f"[locate] no directory containing {'/'.join(MARKER)} was found", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
