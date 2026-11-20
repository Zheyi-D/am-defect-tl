"""Cheap baselines we can report without any of the 66 training runs.

1. majority-class baseline      — no model at all, computed from the frozen test split
2. raw-pixel baseline           — logistic regression on 32x32 grayscale pixels
3. frozen-feature baseline      — frozen MobileNetV2 features + logistic regression

The paper's three Study-Three baselines (MLP / simple CNN / dual-stream CNN) are NOT
reproduced here: they belong to the third dataset, which the authors never released.

Writes results/baselines.csv so the numbers are traceable like every other result.

Run: python tools/make_baselines.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CACHE = Path(
    r"D:\桌面\HKU\IDAT7215 Computer programming for product development and applications"
    r"\_kaggle-build\am-defect-v1"
)

ROWS: list[dict] = []


def _record(baseline: str, dataset: str, split: str, y, pred) -> None:
    from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef

    ROWS.append({
        "baseline": baseline,
        "dataset": dataset,
        "split": split,
        "accuracy": round(float(accuracy_score(y, pred)), 6),
        "f1": round(float(f1_score(y, pred, zero_division=0)), 6),
        "mcc": round(float(matthews_corrcoef(y, pred)), 6),
        "n": int(len(y)),
    })


def _test_labels(ds: str) -> np.ndarray:
    rows = [r for r in csv.DictReader((ROOT / "splits" / f"{ds}.csv").open(encoding="utf-8"))
            if r["split"] == "test"]
    return np.array([1 if r["label"] == "defect" else 0 for r in rows])


def majority_baselines() -> None:
    """Predict one class for every image — the "no model" reference."""
    print("== 1. majority-class baseline (frozen test split) ==")
    for ds in ("D1", "D2"):
        y = _test_labels(ds)
        for guess, name in ((0, "always-nondefect"), (1, "always-defect")):
            pred = np.full_like(y, guess)
            _record(name, ds, "test", y, pred)
            last = ROWS[-1]
            print(f"  {ds} {name:16s} acc={last['accuracy']:.4f}  f1={last['f1']:.4f}  "
                  f"mcc={last['mcc']:.4f}  (n={last['n']})")


def pixel_baseline() -> None:
    """Logistic regression on raw pixels: no pre-training, no CNN."""
    from PIL import Image
    from sklearn.linear_model import LogisticRegression

    print("\n== 2. raw-pixel baseline: logistic regression on 32x32 grayscale (D1) ==")
    rows = list(csv.DictReader((ROOT / "splits" / "D1.csv").open(encoding="utf-8")))
    X, y, s = [], [], []
    for r in rows:
        path = CACHE / r["path"]
        if not path.exists():
            print(f"  missing {path}")
            return
        im = Image.open(path)
        im.draft("L", (256, 256))
        im = im.convert("L").resize((32, 32), Image.BILINEAR)
        X.append(np.asarray(im, dtype=np.float32).ravel() / 255.0)
        y.append(1 if r["label"] == "defect" else 0)
        s.append(r["split"])
    X, y, s = np.stack(X), np.array(y), np.array(s)
    clf = LogisticRegression(max_iter=2000, C=1.0)
    clf.fit(X[s == "train"], y[s == "train"])
    for split in ("val", "test"):
        mask = s == split
        pred = clf.predict(X[mask])
        _record("pixel-logreg-32x32", "D1", split, y[mask], pred)
        last = ROWS[-1]
        print(f"  {split:4s} acc={last['accuracy']:.4f}  f1={last['f1']:.4f}  "
              f"mcc={last['mcc']:.4f}  (n={last['n']})")


def frozen_feature_baseline(model: str = "mobilenet_v2") -> None:
    """Frozen backbone features + logistic regression — isolates the features from the head."""
    import torch
    from PIL import Image
    from sklearn.linear_model import LogisticRegression
    from torchvision import transforms

    from src.models import TransferModel

    print(f"\n== 3. frozen-feature baseline: {model} features + logistic regression (D1) ==")
    net = TransferModel(model, pretrained=True, freeze="all_conv")
    net.eval()
    tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    rows = list(csv.DictReader((ROOT / "splits" / "D1.csv").open(encoding="utf-8")))
    X, y, s = [], [], []
    for r in rows:
        path = CACHE / r["path"]
        if not path.exists():
            print(f"  missing {path}")
            return
        im = Image.open(path)
        im.draft("RGB", (560, 560))          # decode the big JPEG at 1/8 scale
        im = im.convert("RGB")
        with torch.no_grad():
            f = net.net.forward_features(tf(im).unsqueeze(0))
            X.append(f.mean(dim=(2, 3)).squeeze(0).numpy().astype(np.float32))
        y.append(1 if r["label"] == "defect" else 0)
        s.append(r["split"])
        del im

    X, y, s = np.stack(X), np.array(y), np.array(s)
    clf = LogisticRegression(max_iter=3000, C=1.0)
    clf.fit(X[s == "train"], y[s == "train"])
    for split in ("val", "test"):
        mask = s == split
        pred = clf.predict(X[mask])
        _record(f"frozen-{model}-features+logreg", "D1", split, y[mask], pred)
        last = ROWS[-1]
        print(f"  {split:4s} acc={last['accuracy']:.4f}  f1={last['f1']:.4f}  "
              f"mcc={last['mcc']:.4f}  (n={last['n']})")


def write_csv() -> None:
    out = ROOT / "results" / "baselines.csv"
    if not ROWS:
        return
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["baseline", "dataset", "split", "accuracy", "f1", "mcc", "n"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(ROWS, key=lambda r: (r["baseline"], r["dataset"], r["split"])))
    print(f"\n[baselines] wrote {out} ({len(ROWS)} rows)")


def main() -> None:
    majority_baselines()
    for fn in (pixel_baseline, frozen_feature_baseline):
        try:
            fn()
        except Exception as exc:  # torch / timm / memory may be unavailable
            print(f"\n{fn.__name__} skipped: {type(exc).__name__}: {exc}")
    write_csv()


if __name__ == "__main__":
    main()
