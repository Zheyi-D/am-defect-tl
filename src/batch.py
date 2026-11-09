# Author: Lead + agent | Task: batched matrix runs (66 runs) | PR: TBD
# Status: original implementation by this team
"""Run the experiment matrix in batch.

Default matrix = 11 models x 3 optimizers x 2 datasets = 66 runs.
Runs whose metrics.json already exists are skipped automatically (resumable).

Usage:
    # smoke: only vgg16 / D1 / adam, 20 images and 1 epoch
    python -m src.batch --data-root /kaggle/input/datasets/kennethdeng/am-defect-v1 \
        --out results --smoke --limit-runs 1

    # full: the whole matrix
    python -m src.batch --data-root /kaggle/input/datasets/kennethdeng/am-defect-v1 \
        --out results
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .train import load_config, run

MODELS = [
    "vgg16", "vgg19", "resnet50", "resnet101", "inception_resnet_v2",
    "xception", "mobilenet_v2", "efficientnet_b0", "efficientnet_b7",
    "efficientnet_v2m", "nasnet_large",
]
OPTIMIZERS = ["adam", "sgd", "rmsprop"]
DATASETS = ["D1", "D2"]

# Best hyperparameters per dataset (values from the paper's Study One / Study Two, see docs/AUTHOR_CODE.md)
DATASET_HP = {
    "D1": {"batch_size": 8, "epochs": 30},
    "D2": {"batch_size": 32, "epochs": 50},
}


def build_matrix(models, optimizers, datasets) -> list[tuple[str, str, str]]:
    return [(m, d, o) for d in datasets for o in optimizers for m in models]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path, required=True)
    ap.add_argument("--splits-dir", type=Path, default=Path("splits"))
    ap.add_argument("--out", type=Path, default=Path("results"))
    ap.add_argument("--template", type=Path, default=Path("configs/_template.yaml"))
    ap.add_argument("--models", default="all", help="comma-separated, or all")
    ap.add_argument("--datasets", default="all")
    ap.add_argument("--optimizers", default="all")
    ap.add_argument("--limit-runs", type=int, default=None)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--cache-root", type=Path, default=None,
                    help="preprocessed image cache directory (strongly recommended: otherwise every epoch "
                         "decodes the 5184x3456 originals)")
    ap.add_argument("--save-weights", action="store_true", help="save the classification head weights of each run")
    args = ap.parse_args()

    models = MODELS if args.models == "all" else [x.strip() for x in args.models.split(",")]
    datasets = DATASETS if args.datasets == "all" else [x.strip() for x in args.datasets.split(",")]
    optimizers = OPTIMIZERS if args.optimizers == "all" else [x.strip() for x in args.optimizers.split(",")]

    matrix = build_matrix(models, optimizers, datasets)
    if args.limit_runs:
        matrix = matrix[: args.limit_runs]
    print(f"[batch] {len(matrix)} runs in total: {models} x {optimizers} x {datasets}", flush=True)

    base = load_config(args.template)
    done, failed = [], []
    for i, (model, dataset, optimizer) in enumerate(matrix, 1):
        cfg = dict(base)
        cfg.update({"model": model, "dataset": dataset, "optimizer": optimizer,
                    **DATASET_HP[dataset]})
        if args.save_weights:
            cfg["save_weights"] = True
        print(f"\n[batch] ({i}/{len(matrix)}) {model} / {dataset} / {optimizer}", flush=True)
        try:
            run(cfg, args.data_root, args.splits_dir, args.out,
                smoke=args.smoke, force=args.force, cache_root=args.cache_root)
            done.append(f"{model}__{dataset}__{optimizer}")
        except Exception as exc:  # a single failed run does not abort the whole batch
            print(f"[batch][ERROR] {model}/{dataset}/{optimizer}: {type(exc).__name__}: {exc}", flush=True)
            failed.append({"run": f"{model}__{dataset}__{optimizer}", "error": str(exc)})

    print(f"\n[batch] finished {len(done)}, failed {len(failed)}", flush=True)
    if failed:
        summary = Path(args.out) / "batch_failures.json"
        summary.parent.mkdir(parents=True, exist_ok=True)
        summary.write_text(json.dumps(failed, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[batch] failure list: {summary}", flush=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
