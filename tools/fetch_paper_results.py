# Author: foundation team | Task: extract the 99 result tables from the authors' repository to build the benchmark baseline | PR: #<number>
# Status: original implementation by this group (the authors' repository only has xlsx files, no reusable code)
"""Extract the 99 xlsx files (3 studies x 3 optimizers x 11 models) in the authors' AM3d repository into one comparison table.

Why it is needed:
  - The 66 runs produced by 8 people must be compared cell by cell with the paper values, which would take a week to copy by hand;
  - The paper body (paywalled) has no full table, but the xlsx files in the authors' repository hold the complete metrics.

Output: docs/paper_results.csv
  Columns: dataset,optimizer,model,split,accuracy,precision,recall,f1,mcc,kappa,auc,map,sensitivity,specificity,source_url
  Dataset mapping: Studyone->D1, Studytwo->D2, Studythree->D3 (the authors never released the data)

Usage:
    python tools/fetch_paper_results.py            # needs network, about 1-2 minutes
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

REPO = "mahsan2/AM3d"
BRANCH = "main"
API = f"https://api.github.com/repos/{REPO}/contents"
RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/"
UA = {"User-Agent": "am-defect-tl"}

STUDY_MAP = {"Studyone": "D1", "Studytwo": "D2", "Studythree": "D3"}
OPT_MAP = {"Adam": "adam", "Sgd": "sgd", "rmsprop": "rmsprop"}
SPLIT_MAP = {"Train": "train", "Validation": "val", "Test": "test"}

# Filename prefix -> the model field in configs/*.yaml
MODEL_PATTERNS = [
    ("inceptionresnet", "inception_resnet_v2"),
    ("mobilenet", "mobilenet_v2"),
    ("nasnetlargemodel", "nasnet_large"),
    ("nasnetlarge", "nasnet_large"),
    ("netb0", "efficientnet_b0"),
    ("netb7", "efficientnet_b7"),
    ("v2m", "efficientnet_v2m"),
    ("resnet101", "resnet101"),
    ("resnet50", "resnet50"),
    ("vgg16", "vgg16"),
    ("vgg19", "vgg19"),
    ("xception", "xception"),
]

METRIC_ORDER = [
    "accuracy", "precision", "recall", "f1", "mcc", "kappa",
    "auc", "map", "sensitivity", "specificity",
]


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=60).read()


def list_dir(path: str) -> list[dict]:
    return json.loads(_get(f"{API}/{path}?ref={BRANCH}"))


def model_key(filename: str) -> str | None:
    stem = re.sub(r"model_results\.xlsx$", "", filename, flags=re.I).lower()
    for pattern, key in MODEL_PATTERNS:
        if stem.startswith(pattern):
            return key
    return None


def parse_xlsx(blob: bytes) -> list[dict]:
    """Read the Metrics sheet and return 3 records (train / val / test)."""
    try:
        import openpyxl
    except ImportError:  # pragma: no cover
        sys.exit("openpyxl is required: pip install openpyxl")

    wb = openpyxl.load_workbook(io.BytesIO(blob), data_only=True)
    if "Metrics" not in wb.sheetnames:
        return []
    ws = wb["Metrics"]

    header = [str(c.value).strip() if c.value else "" for c in ws[1]]
    # The header looks like ['', 'Accuracy', 'Precision', ...]; build column name -> column index
    col = {}
    for idx, name in enumerate(header):
        key = name.lower().replace(" ", "").replace("-", "")
        alias = {
            "f1score": "f1", "accuracy": "accuracy", "precision": "precision",
            "recall": "recall", "mcc": "mcc", "kappa": "kappa", "auc": "auc",
            "map": "map", "sensitivity": "sensitivity", "specificity": "specificity",
        }
        if key in alias:
            col[alias[key]] = idx

    rows_out = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[0] not in SPLIT_MAP:
            continue
        rec = {"split": SPLIT_MAP[str(row[0]).strip()]}
        for metric in METRIC_ORDER:
            idx = col.get(metric)
            value = row[idx] if idx is not None and idx < len(row) else None
            try:
                rec[metric] = round(float(value), 4)
            except (TypeError, ValueError):
                rec[metric] = ""
        rows_out.append(rec)
    return rows_out


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "docs" / "paper_results.csv"
    records: list[dict] = []
    missing: list[str] = []

    for study_dir, dataset in STUDY_MAP.items():
        for opt_dir, optimizer in OPT_MAP.items():
            listing = list_dir(f"{study_dir}/{opt_dir}")
            for item in listing:
                name = item["name"]
                if not name.lower().endswith("model_results.xlsx"):
                    continue
                model = model_key(name)
                if model is None:
                    missing.append(f"{study_dir}/{opt_dir}/{name}")
                    continue
                blob = _get(RAW + f"{study_dir}/{opt_dir}/{name}")
                for rec in parse_xlsx(blob):
                    records.append({
                        "dataset": dataset, "optimizer": optimizer, "model": model,
                        **rec, "source_url": f"https://github.com/{REPO}/blob/{BRANCH}/{study_dir}/{opt_dir}/{name}",
                    })

    fields = ["dataset", "optimizer", "model", "split", *METRIC_ORDER, "source_url"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)

    print(f"wrote {out} : {len(records)} rows "
          f"(expected 3 studies x 3 optimizers x 11 models x 3 splits = 297)")
    if missing:
        print("unrecognised files (add them to MODEL_PATTERNS):")
        for m in missing:
            print("  -", m)


if __name__ == "__main__":
    main()
