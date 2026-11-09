# Author: Lead + agent | Task: image preprocessing cache | PR: TBD
# Status: original implementation by this team
"""Downscale the original images to the target size once and cache them, so every epoch avoids
repeatedly decoding large images.

Why this is needed:
    The original D1 images are 5184x3456 (3 MB each); decoding one on CPU takes about 0.3 s, so an epoch
    of 271 images costs about 80 s, and 30 epochs mean 40 minutes per run -- 66 runs would never finish.
    After preprocessing to 224x224 an epoch takes only 1-2 seconds.

Rules (matching the authors' implementation: resize directly, ignoring aspect ratio):
    D1: 5184x3456 -> 224x224
    D2: 128x128   -> 224x224
    Everything is saved as JPEG (quality=92) and keeps the original file stem.

Usage:
    python -m src.data_prepare --data-root <raw data root> --out /kaggle/working/cache --size 224
"""

from __future__ import annotations

import argparse
from pathlib import Path

DATASETS = ["D1", "D2"]
LABELS = ["defect", "nondefect"]


def prepare_one(src: Path, dst: Path, size: int, quality: int = 92) -> bool:
    """Return True if a file was actually written, False if it was skipped (already exists)."""
    if dst.exists():
        return False
    from PIL import Image

    img = Image.open(src)
    # draft: let the JPEG decoder downsample by 1/2, 1/4 or 1/8 while decoding; large images get 5-8x faster
    img.draft("RGB", (size * 2, size * 2))
    img = img.convert("RGB").resize((size, size), Image.BILINEAR)
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, format="JPEG", quality=quality)
    return True


def prepare(data_root: Path, out_dir: Path, size: int = 224, quality: int = 92) -> dict:
    stats = {}
    for ds in DATASETS:
        written = skipped = 0
        for label in LABELS:
            src_dir = Path(data_root) / "data" / ds / label
            if not src_dir.is_dir():
                raise FileNotFoundError(f"directory not found: {src_dir}")
            files = sorted(p for p in src_dir.iterdir() if p.is_file())
            for i, f in enumerate(files, 1):
                dst = Path(out_dir) / ds / label / f"{f.stem}.jpg"
                if prepare_one(f, dst, size, quality):
                    written += 1
                else:
                    skipped += 1
                if i % 500 == 0:
                    print(f"[prepare] {ds}/{label} {i}/{len(files)}", flush=True)
        stats[ds] = {"written": written, "skipped": skipped}
        print(f"[prepare] {ds}: wrote {written}, skipped {skipped} (cache already present)", flush=True)
    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--size", type=int, default=224)
    ap.add_argument("--quality", type=int, default=92)
    args = ap.parse_args()

    stats = prepare(args.data_root, args.out, args.size, args.quality)
    total = sum(s["written"] + s["skipped"] for s in stats.values())
    print(f"[prepare] done, {total} images in total, cache directory: {args.out}")


if __name__ == "__main__":
    main()
