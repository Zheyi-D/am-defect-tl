# Author: Lead + agent | Task: dataset and transforms | PR: TBD
# Status: original implementation by this team. Reference: torchvision.transforms docs (calls only)
"""Read images according to the splits csv and return (image_tensor, label).

Preprocessing mirrors the authors' implementation: resize directly to 224x224 (ignoring aspect ratio),
then normalize with the ImageNet mean/std.
(The authors use Keras + /255; we use the standard torchvision normalization, and the difference is
documented in the report's limitations section.)
"""

from __future__ import annotations

import csv
from pathlib import Path

import torch
from torch.utils.data import Dataset

LABEL_TO_IDX = {"nondefect": 0, "defect": 1}
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def read_split(csv_path: Path, split: str) -> list[dict]:
    with Path(csv_path).open(encoding="utf-8", newline="") as fh:
        return [r for r in csv.DictReader(fh) if r["split"] == split]


def build_transform(input_size: int, train: bool, augment: bool):
    from torchvision import transforms

    ops = [transforms.Resize((input_size, input_size))]
    if train and augment:
        ops.append(transforms.RandomRotation(15))
    ops += [transforms.ToTensor(), transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD)]
    return transforms.Compose(ops)


class AMDefectDataset(Dataset):
    def __init__(self, rows: list[dict], data_root: Path, input_size: int = 224,
                 train: bool = False, augment: bool = False, limit: int | None = None,
                 cache_root: Path | None = None):
        from PIL import Image  # noqa: F401  (confirms that Pillow is importable)

        self.rows = rows[:limit] if limit else rows
        self.data_root = Path(data_root)
        self.cache_root = Path(cache_root) if cache_root else None
        self.transform = build_transform(input_size, train, augment)

    def _resolve(self, rel_path: str) -> Path:
        """data/D1/defect/x.JPG -> cache path <cache>/D1/defect/x.jpg (when a cache root is given)."""
        rel = str(rel_path).replace("\\", "/")
        if self.cache_root is None:
            return self.data_root / rel
        parts = rel.split("/")
        if len(parts) < 4 or parts[0] != "data":
            return self.data_root / rel
        _, ds, label, fname = parts[0], parts[1], parts[2], "/".join(parts[3:])
        return self.cache_root / ds / label / f"{Path(fname).stem}.jpg"

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int):
        from PIL import Image

        r = self.rows[idx]
        img_path = self._resolve(r["path"])
        img = Image.open(img_path).convert("RGB")
        return self.transform(img), torch.tensor(LABEL_TO_IDX[r["label"]], dtype=torch.long)


def class_counts(rows: list[dict]) -> dict:
    out = {"defect": 0, "nondefect": 0}
    for r in rows:
        out[r["label"]] += 1
    return out
