# Author: Kenneth + agent | Task: no-transfer ablation (is the ImageNet weight doing the work?)
# Status: new script, does not touch the existing 66 runs
"""No-transfer ablation: how much of the accuracy comes from the pretrained weights?

Three configurations, identical data / head / hyper-parameters, only the backbone init differs:

    transfer      ImageNet weights + frozen convolution   (our main method, already have it)
    rand_frozen   random init + frozen convolution        (isolates "pretrained weights" alone)
    rand_full     random init + every parameter trainable (the from-scratch baseline)

This script only runs the two NEW configurations and writes them to a separate
output directory, so `results/` and `leaderboard.csv` stay untouched.

Usage:
    python tools/run_ablation.py --data-root <DIR> --cache-root <CACHE> \
        --out results_ablation --models mobilenet_v2 --datasets D1,D2 \
        --optimizers adam,sgd,rmsprop
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CONFIGS = {
    "rand_frozen": {"pretrained": False, "freeze": "all_conv"},
    "rand_full": {"pretrained": False, "freeze": "none"},
}


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the no-transfer ablation.")
    ap.add_argument("--data-root", type=Path, required=True)
    ap.add_argument("--cache-root", type=Path, default=None)
    ap.add_argument("--splits-dir", type=Path, default=ROOT / "splits")
    ap.add_argument("--out", type=Path, default=ROOT / "results_ablation")
    ap.add_argument("--models", default="mobilenet_v2")
    ap.add_argument("--datasets", default="D1,D2")
    ap.add_argument("--optimizers", default="adam,sgd,rmsprop")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    import sys

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from src.batch import DATASET_HP
    from src.train import load_config, run

    template = ROOT / "configs" / "_template.yaml"
    base = load_config(template)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    datasets = [d.strip() for d in args.datasets.split(",") if d.strip()]
    optimizers = [o.strip() for o in args.optimizers.split(",") if o.strip()]

    total = len(models) * len(datasets) * len(optimizers) * len(CONFIGS)
    done = 0
    failures: list[str] = []

    for init_name, init_cfg in CONFIGS.items():
        for dataset in datasets:
            for model in models:
                for optimizer in optimizers:
                    done += 1
                    run_id = f"{model}__{dataset}__{optimizer}__{init_name}__s{args.seed}"
                    cfg = dict(base)
                    cfg.update(init_cfg)
                    cfg.update({
                        "model": model,
                        "dataset": dataset,
                        "optimizer": optimizer,
                        "seed": args.seed,
                        "run_tag": init_name,
                        **DATASET_HP[dataset],
                    })
                    print(f"\n[ablation] ({done}/{total}) {run_id}", flush=True)
                    try:
                        run(cfg, args.data_root, args.splits_dir, args.out,
                            smoke=args.smoke, force=args.force, cache_root=args.cache_root)
                    except Exception as exc:  # keep going, report at the end
                        failures.append(f"{run_id}: {type(exc).__name__}: {exc}")
                        print(f"[ablation] FAILED {run_id}: {exc}", flush=True)

    print(f"\n[ablation] finished {total - len(failures)}/{total}")
    for f in failures:
        print("  failed:", f)


if __name__ == "__main__":
    main()
