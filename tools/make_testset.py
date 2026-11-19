# Author: Kenneth | Task: rebuild testset/ from the frozen splits
"""Copy every test-split image of D1 and D2 into one folder (`testset/`).

Source of truth for "which image is test": the frozen split files
`splits/D1.csv` and `splits/D2.csv`. Images themselves live outside the repo
(Kaggle dataset mount, or the local copy used to build it).

Usage:
    python tools/make_testset.py                       # default source path
    python tools/make_testset.py --data-root <DIR>     # Kaggle mount:
                                                       #   /kaggle/input/datasets/<owner>/<slug>
                                                       #   or the local copy ending in .../am-defect-v1
    python tools/make_testset.py --out testset --copy   # also copy the files

Idempotent: re-running overwrites the same destination files and rewrites
`testset/manifest.csv`.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = Path(r"D:\桌面\HKU\IDAT7215 Computer programming for product development and applications\_kaggle-build\am-defect-v1")
DATASETS = ("D1", "D2")


def main() -> None:
    ap = argparse.ArgumentParser(description="Collect all test-split images into one folder.")
    ap.add_argument("--data-root", type=Path, default=DEFAULT_DATA,
                    help="directory that contains data/{D1,D2}/{defect,nondefect}")
    ap.add_argument("--out", type=Path, default=ROOT / "testset")
    ap.add_argument("--copy", action="store_true", default=True, help="copy files (default)")
    ap.add_argument("--no-copy", dest="copy", action="store_false", help="only write the manifest")
    args = ap.parse_args()

    data_root = args.data_root
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    missing: list[str] = []

    for ds in DATASETS:
        split_csv = ROOT / "splits" / f"{ds}.csv"
        if not split_csv.exists():
            raise SystemExit(f"missing split file: {split_csv}")
        with split_csv.open(encoding="utf-8") as fh:
            test_rows = [r for r in csv.DictReader(fh) if r["split"] == "test"]
        for r in test_rows:
            src = data_root / r["path"]
            if not src.exists():
                missing.append(str(src))
                continue
            entry = {
                "dataset": ds,
                "label": r["label"],
                "split": "test",
                "file": f"{ds}/test/{r['label']}/{src.name}",
                "source_id": r.get("source_id", ""),
                "bytes": src.stat().st_size,
            }
            if args.copy:
                dst_dir = out / ds / "test" / r["label"]
                dst_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst_dir / src.name)
            rows.append(entry)

    manifest = out / "manifest.csv"
    with manifest.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["dataset", "label", "split", "file", "source_id", "bytes"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(rows, key=lambda x: x["file"]))

    counts = Counter((r["dataset"], r["label"]) for r in rows)
    total_mb = sum(r["bytes"] for r in rows) / 1024 / 1024
    print(f"[testset] {out}  ({len(rows)} files, {total_mb:.1f} MB)")
    for key in sorted(counts):
        print(f"  {key[0]} / {key[1]:<10} {counts[key]:>4}")
    if missing:
        print(f"[testset] WARNING: {len(missing)} source files missing, e.g. {missing[0]}")
        print("[testset] pass --data-root to point at the dataset root (needs data/D1/... layout)")


if __name__ == "__main__":
    main()
