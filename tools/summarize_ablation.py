# Author: Kenneth + agent | Task: build the no-transfer ablation table
"""Summarise the no-transfer ablation into one table for the report.

Reads:
    results_ablation/runs/<model>__<dataset>__<optimizer>__<tag>__s<seed>/metrics.json
    results/runs/<model>__<dataset>__<optimizer>__s<seed>/metrics.json        (transfer reference)

Writes:
    results_ablation/ABLATION.md     (markdown table, ready to paste)

Usage:
    python tools/summarize_ablation.py
    python tools/summarize_ablation.py --ablation results_ablation --main results
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INITS = {
    "transfer": "ImageNet pretrained + frozen conv (main method)",
    "rand_frozen": "random init + frozen conv (weights only)",
    "rand_full": "random init + all parameters trainable (from scratch)",
}
METRICS = ("accuracy", "f1", "mcc")


def load_runs(root: Path) -> list[dict]:
    out = []
    runs = root / "runs"
    if not runs.exists():
        return out
    for run_dir in sorted(runs.iterdir()):
        mf = run_dir / "metrics.json"
        if not mf.exists():
            continue
        try:
            m = json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            continue
        parts = run_dir.name.split("__")
        if len(parts) < 4:
            continue
        model, dataset, optimizer = parts[0], parts[1], parts[2]
        init = "transfer" if len(parts) == 4 else parts[3]
        test = (m.get("metrics") or {}).get("test") or {}
        if not test:
            continue
        out.append({
            "model": model, "dataset": dataset, "optimizer": optimizer,
            "init": init, "test": test, "run_id": run_dir.name,
        })
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Summarise the no-transfer ablation.")
    ap.add_argument("--ablation", type=Path, default=ROOT / "results_ablation")
    ap.add_argument("--main", type=Path, default=ROOT / "results")
    ap.add_argument("--model", default="mobilenet_v2",
                    help="only this backbone is used in the ablation table")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    rows = load_runs(args.ablation) + load_runs(args.main)
    rows = [r for r in rows if r["model"] == args.model]
    if not rows:
        raise SystemExit("no runs found — did the kernel finish and get downloaded?")

    # mean over optimisers for each (dataset, init)
    bucket: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        bucket[(r["dataset"], r["init"])].append(r)

    lines = [
        f"# No-transfer ablation — {args.model}",
        "",
        "All cells are the **mean over the three optimisers** (Adam / SGD / RMSprop), "
        "same splits, same head, same hyper-parameters; only the backbone initialisation differs.",
        "",
        "| Configuration | " + " | ".join(f"{d} {' / '.join(METRICS)}" for d in ("D1", "D2")) + " |",
        "|---|" + "|".join(["---"] * 2) + "|",
    ]
    for init in ("transfer", "rand_frozen", "rand_full"):
        cells = []
        for dataset in ("D1", "D2"):
            rs = bucket.get((dataset, init), [])
            if not rs:
                cells.append("—")
                continue
            vals = []
            for k in METRICS:
                mean = sum(float(r["test"].get(k) or 0.0) for r in rs) / len(rs)
                vals.append(f"{mean:.4f}")
            cells.append(" / ".join(vals) + f"  (n={len(rs)})")
        lines.append(f"| {INITS[init]} | " + " | ".join(cells) + " |")

    lines += ["", "## Per-run detail", "",
              "| dataset | init | optimizer | accuracy | f1 | mcc |",
              "|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda x: (x["dataset"], x["init"], x["optimizer"])):
        lines.append(
            f"| {r['dataset']} | {r['init']} | {r['optimizer']} | "
            f"{float(r['test'].get('accuracy') or 0):.4f} | "
            f"{float(r['test'].get('f1') or 0):.4f} | "
            f"{float(r['test'].get('mcc') or 0):.4f} |"
        )

    text = "\n".join(lines) + "\n"
    out = args.out or (args.ablation / "ABLATION.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")
    print(text)
    print(f"[ablation] written -> {out}")


if __name__ == "__main__":
    main()
