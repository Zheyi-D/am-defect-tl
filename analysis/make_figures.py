# Author: jellyfishhamburger | Task: T1 report figure generator | PR: pending
# Status: original implementation. Reads results/ only; never modifies metrics.json / leaderboard.csv.
"""Generate the global summary figures needed by report Section 3 (T1).

Inputs (read-only):
    results/leaderboard.csv
    results/runs/*/metrics.json
    results/runs/*/confusion_matrices.json

Outputs:
    results/figures/fig_accuracy_by_model.png   accuracy for 11 models × 2 datasets (with reported values)
    results/figures/fig_optimizer_heatmap.png   optimizer-ablation heatmap
    results/figures/fig_confusion_grid.png      confusion matrices of 4 representative runs
    results/figures/fig_delta_acc.png           accuracy gap (ours − reported)
    results/figures/fig_ranking.png             model accuracy ranking
    results/figures/INDEX.md                    figure number / file / one-line description

Usage:
    python -m analysis.make_figures                 # redraw everything
    python -m analysis.make_figures --only 1,3      # only the listed figure numbers
    python -m analysis.make_figures --dpi 300

Constraint: every number is read directly from repo files; no hard-coded constants appear in the figures
(except reported values, which come from the paper_acc column of leaderboard.csv).
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGDIR = RESULTS / "figures"

# Display names shared with the dashboard/report (figures always use English)
DISPLAY = {
    "vgg16": "VGG16", "vgg19": "VGG19", "resnet50": "ResNet50", "resnet101": "ResNet101",
    "inception_resnet_v2": "InceptionResNetV2", "xception": "Xception",
    "mobilenet_v2": "MobileNetV2", "efficientnet_b0": "EfficientNet-B0",
    "efficientnet_b7": "EfficientNet-B7", "efficientnet_v2m": "EfficientNetV2-M",
    "nasnet_large": "NASNet-Large",
}
# Model order used in the paper (roughly increasing parameter count); kept fixed for comparability
ORDER = ["mobilenet_v2", "efficientnet_b0", "resnet50", "xception", "inception_resnet_v2",
         "efficientnet_v2m", "efficientnet_b7", "resnet101", "vgg16", "vgg19", "nasnet_large"]
DATASETS = ["D1", "D2"]
OPTS = ["adam", "sgd", "rmsprop"]

C_D1, C_D2 = "#16233A", "#BF452C"
C_PAPER = "#8C8175"
C_ACCENT = "#2A6B57"
GREY = "#6B7280"

# Filled in by main(); importing matplotlib at module import time is avoided (CI has no matplotlib/torch)
plt = None


# ---------------------------------------------------------------- data
def read_leaderboard() -> list[dict]:
    with (RESULTS / "leaderboard.csv").open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for k in ("accuracy", "f1", "mcc", "paper_acc", "paper_f1", "delta_acc",
                  "n_params_trainable", "train_time_s"):
            if r.get(k) in ("", None):
                r[k] = None
            else:
                r[k] = float(r[k])
    return rows


def load_metrics(run_id: str) -> dict:
    p = RESULTS / "runs" / run_id / "metrics.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def load_cm(run_id: str) -> dict:
    p = RESULTS / "runs" / run_id / "confusion_matrices.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def pick(rows, model, dataset, opt="adam"):
    for r in rows:
        if r["model"] == model and r["dataset"] == dataset and r["optimizer"] == opt:
            return r
    return None


def style(plt):
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#9AA0A6",
        "axes.labelcolor": "#1F2937",
        "text.color": "#111827",
        "grid.color": "#E5E0D5",
        "grid.linewidth": 0.7,
        "legend.frameon": False,
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })


# ---------------------------------------------------------------- figures
def fig_accuracy(models, rows, out: Path):
    """① Test accuracy of 11 models × 2 datasets, overlaid with the reported values."""
    import numpy as np

    fig, ax = plt.subplots(figsize=(9.2, 3.6))
    x = np.arange(len(models))
    w = 0.36
    for i, (ds, color) in enumerate(zip(DATASETS, (C_D1, C_D2))):
        vals = [(pick(rows, m, ds) or {}).get("accuracy") for m in models]
        vals = [v if v is not None else 0 for v in vals]
        ax.bar(x + (i - 0.5) * w, vals, w, color=color, label=f"{ds} (ours, Adam)", zorder=2)
        paper = [((pick(rows, m, ds) or {}).get("paper_acc")) for m in models]
        px = [xi + (i - 0.5) * w for xi, p in zip(x, paper) if p is not None]
        py = [p for p in paper if p is not None]
        ax.scatter(px, py, marker="_", s=170, linewidths=1.8, color=C_PAPER,
                   label="reported by authors" if i == 0 else None, zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels([DISPLAY.get(m, m) for m in models], rotation=28, ha="right")
    ax.set_ylabel("Test accuracy")
    ax.set_ylim(0.40, 1.03)
    ax.set_yticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.grid(axis="y", zorder=0)
    ax.set_axisbelow(True)
    ax.set_title("Test accuracy by backbone and dataset (Adam, seed 42)", pad=26)
    ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.005), fontsize=7.6)
    fig.savefig(out / "fig_accuracy_by_model.png")
    plt.close(fig)


def fig_heatmap(models, rows, out: Path):
    """② Optimizer ablation heatmap (D1 / D2 panels, 11 models × 3 optimizers, shared colour scale)."""
    import numpy as np

    grids = []
    for ds in DATASETS:
        grid = np.full((len(models), len(OPTS)), np.nan)
        for i, m in enumerate(models):
            for j, o in enumerate(OPTS):
                r = pick(rows, m, ds, o)
                if r and r["accuracy"] is not None:
                    grid[i, j] = r["accuracy"]
        grids.append(grid)
    finite = np.concatenate([g[~np.isnan(g)] for g in grids])
    vmin = np.floor(finite.min() * 100) / 100 if finite.size else 0.85
    mid = (vmin + 1.0) / 2

    fig, axes = plt.subplots(1, 2, figsize=(8.4, 4.2), sharey=True)
    for ax, ds, grid in zip(axes, DATASETS, grids):
        im = ax.imshow(grid, cmap="viridis", vmin=vmin, vmax=1.0, aspect="auto")
        for i in range(len(models)):
            for j in range(len(OPTS)):
                v = grid[i, j]
                if np.isnan(v):
                    continue
                ax.text(j, i, f"{v:.3f}", ha="center", va="center", fontsize=7.4,
                        color="white" if v < mid + 0.01 else "#111827")
        ax.set_xticks(range(len(OPTS)))
        ax.set_xticklabels([{"adam": "Adam", "sgd": "SGD", "rmsprop": "RMSprop"}[o] for o in OPTS])
        ax.set_yticks(range(len(models)))
        ax.set_yticklabels([DISPLAY.get(m, m) for m in models])
        ax.set_title(f"{ds} — test accuracy")
        ax.tick_params(length=0)
        for sp in ax.spines.values():
            sp.set_visible(False)
    cb = fig.colorbar(im, ax=axes, fraction=0.025, pad=0.02)
    cb.set_label(f"Test accuracy (colour scale {vmin:.2f}–1.00, shared by both panels)", fontsize=7.5)
    cb.outline.set_visible(False)
    fig.suptitle("Optimizer ablation: frozen backbone, head-only training (lr=1e-3, 30 epochs)", fontsize=10)
    fig.savefig(out / "fig_optimizer_heatmap.png")
    plt.close(fig)


def fig_confusion(models, rows, out: Path):
    """③ Test-set confusion matrices of 4 representative runs."""
    import numpy as np

    # Representative runs: best D1 / worst D1 / best D2 / worst D2 (by test accuracy)
    d1 = [r for r in rows if r["dataset"] == "D1" and r["accuracy"] is not None]
    d2 = [r for r in rows if r["dataset"] == "D2" and r["accuracy"] is not None]
    d1.sort(key=lambda r: r["accuracy"])
    d2.sort(key=lambda r: r["accuracy"])
    picks = [d1[-1], d1[0], d2[-1], d2[0]]

    fig, axes = plt.subplots(2, 2, figsize=(6.6, 5.6))
    for ax, r in zip(axes.ravel(), picks):
        cm = load_cm(r["run_id"]).get("test")
        if not cm:
            ax.axis("off")
            continue
        arr = np.array(cm)
        ax.imshow(arr, cmap="Blues", vmin=0, vmax=arr.max() * 1.15)
        for (i, j), v in np.ndenumerate(arr):
            ax.text(j, i, str(int(v)), ha="center", va="center", fontsize=11,
                    color="white" if v > arr.max() * 0.55 else "#111827")
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["nondefect", "defect"])
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["nondefect", "defect"])
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        ax.set_title(f"{DISPLAY.get(r['model'], r['model'])} · {r['dataset']} · {r['optimizer'].upper()}\n"
                     f"acc={r['accuracy']:.3f}  f1={r['f1']:.3f}", fontsize=8.5)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
    fig.suptitle("Confusion matrices: best and worst runs per dataset (test split)", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "fig_confusion_grid.png")
    plt.close(fig)


def fig_delta(models, rows, out: Path):
    """④ Accuracy gap (ours − reported)."""
    import numpy as np

    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.9), sharex=True)
    # sharex=True: both panels share the x axis, so set the range once from the global extremes
    allv = [r["delta_acc"] for r in rows if r["delta_acc"] is not None]
    lo, hi = min(-0.09, min(allv) - 0.04), max(0.05, max(allv) * 1.18)
    for ax, ds in zip(axes, DATASETS):
        data = []
        for m in models:
            r = pick(rows, m, ds)
            if r and r["delta_acc"] is not None:
                data.append((r["model"], r["delta_acc"], r["paper_f1"]))
        data.sort(key=lambda t: t[1])
        names = [DISPLAY.get(m, m) for m, _, _ in data]
        vals = [v for _, v, _ in data]
        colors = [C_D1 if ds == "D1" else C_D2] * len(vals)
        bars = ax.barh(np.arange(len(vals)), vals, color=colors, height=0.62, zorder=2)
        ax.axvline(0, color="#111827", linewidth=0.9, zorder=3)
        ax.set_yticks(np.arange(len(vals)))
        ax.set_yticklabels(names)
        ax.set_title(f"{ds}")
        ax.set_xlabel("Δ accuracy (ours − authors)")
        ax.grid(axis="x", zorder=0)
        ax.set_axisbelow(True)
        for b, (_, v, pf1) in zip(bars, data):
            # Put labels for negative values on the right of the zero line too: a small negative bar is
            # only a few pixels wide, so a left-hand label would overlap the model names
            ax.text((v if v > 0 else 0) + 0.008, b.get_y() + b.get_height() / 2, f"{v:+.3f}",
                    va="center", ha="left", fontsize=7.0,
                    color="#111827", clip_on=False,
                    bbox=None if pf1 != 0 else dict(boxstyle="round,pad=0.12", fc="#F3D3CB",
                                                    ec="none", alpha=0.95))
    axes[0].set_xlim(lo, hi)
    fig.suptitle("Reproduction gap vs. Ahsan et al. (2024) — Adam runs", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "fig_delta_acc.png")
    plt.close(fig)


def fig_ranking(models, rows, out: Path):
    """⑤ Model accuracy ranking (best of the three optimizers per model)."""
    import numpy as np

    data = []
    for m in models:
        best = {}
        for ds in DATASETS:
            cand = [r for r in rows if r["model"] == m and r["dataset"] == ds and r["accuracy"] is not None]
            best[ds] = max(cand, key=lambda r: r["accuracy"]) if cand else None
        data.append((m, best))
    data.sort(key=lambda t: -((t[1]["D1"]["accuracy"] if t[1]["D1"] else 0)))

    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    y = np.arange(len(data))
    for i, (m, best) in enumerate(data):
        r1, r2 = best["D1"], best["D2"]
        if r1 and r2:
            ax.plot([r1["accuracy"], r2["accuracy"]], [i, i], color="#D5CCB8", linewidth=1.4, zorder=1)
        if r1:
            ax.scatter(r1["accuracy"], i, s=42, color=C_D1, zorder=3, label="D1" if i == 0 else None)
        if r2:
            ax.scatter(r2["accuracy"], i, s=42, color=C_D2, zorder=3, label="D2" if i == 0 else None)
        if r1:
            ax.annotate({"adam": "Adam", "sgd": "SGD", "rmsprop": "RMSprop"}[r1["optimizer"]],
                        xy=(1.012, i), xycoords=("axes fraction", "data"),
                        va="center", ha="left", fontsize=6.8, color=GREY,
                        annotation_clip=False)
    ax.set_yticks(y)
    ax.set_yticklabels([DISPLAY.get(m, m) for m, _ in data])
    ax.invert_yaxis()          # best on top (matplotlib's y=0 is at the bottom by default)
    ax.set_xlabel("Test accuracy (best of 3 optimizers)")
    ax.set_xlim(0.90, 1.005)
    ax.grid(axis="x", zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc="lower left", fontsize=8)
    ax.set_title("Model ranking on D1 and D2 (best of 3 optimizers)")
    ax.annotate("best\noptimizer", xy=(1.012, 1.0), xycoords=("axes fraction", "axes fraction"),
                va="bottom", ha="left", fontsize=6.2, color=GREY, annotation_clip=False)
    fig.savefig(out / "fig_ranking.png")
    plt.close(fig)


INDEX_ROWS = [
    ("Figure 1", "fig_accuracy_by_model.png",
     "Test accuracy of 11 ImageNet backbones on D1 and D2 (Adam, seed 42). Bars are our runs; short horizontal ticks "
     "are the values reported by Ahsan et al. (2024). The y-axis starts at 0.40.",
     "① Accuracy bars for 11 models × 2 datasets; short ticks are reported values. The y-axis starts at 0.40, "
     "so mind the truncated scale when reading."),
    ("Figure 2", "fig_optimizer_heatmap.png",
     "Optimizer ablation: test accuracy of each backbone under Adam / SGD / RMSprop with a frozen backbone and "
     "head-only training (lr = 1e-3, 30 epochs). Colour scale spans the observed range.",
     "② Optimizer ablation heatmap (D1 / D2 panels); the colour scale is stretched to the observed minimum."),
    ("Figure 3", "fig_confusion_grid.png",
     "Confusion matrices of the best and worst run per dataset (test split). Rows = true label, columns = predicted; "
     "each panel is shaded to its own maximum.",
     "③ Confusion matrices of 4 representative runs (best / worst per dataset)."),
    ("Figure 4", "fig_delta_acc.png",
     "Accuracy gap between our reproduction and the reported values (Adam runs). Pink labels mark the authors' "
     "EfficientNet-B0 / B7 / V2-M rows, whose reported F1 is 0.000 (majority-class collapse, D1 accuracy 0.4909) — "
     "those gaps are not evidence that our implementation is better.",
     "④ Our Δaccuracy vs. the paper; light-red labels mark the three rows where the authors collapsed to the "
     "majority class."),
    ("Figure 5", "fig_ranking.png",
     "Model ranking by test accuracy (best of the three optimizers). The line joins the best D1 and D2 run of each "
     "backbone; the right-hand column names the optimizer that produced the D1 best run. D1 test n=54, so ties "
     "within ~0.02 are not statistically meaningful.",
     "⑤ Model accuracy ranking; the right-hand column names the optimizer behind the best D1 run."),
]


def write_index(out: Path, made: list[str]):
    lines = [
        "# Figure index (figures used in report Section 3)",
        "",
        "> Generated by `python -m analysis.make_figures`; **do not edit by hand**. All numbers are read from",
        "> `results/leaderboard.csv` and `results/runs/*/{metrics,confusion_matrices}.json`; reported values come",
        "> from `docs/paper_results.csv`.",
        "",
        "| Figure | File | Caption (EN) | Notes |",
        "|---|---|---|---|",
    ]
    for no, fname, cap, notes in INDEX_ROWS:
        mark = "" if (out / fname).exists() else " *(not generated)*"
        lines.append(f"| {no} | [`{fname}`]({fname}){mark} | {cap} | {notes} |")
    lines += [
        "",
        "## Commands",
        "",
        "```bash",
        "python -m analysis.make_figures            # everything",
        "python -m analysis.make_figures --only 1,3 # figures 1 and 3 only",
        "```",
        "",
        "## Conventions and known issues",
        "",
        "- Figures 1 and 4 compare **Adam** runs against the authors' Adam rows; each model is compared under the",
        "  same optimizer, so we never pit our best run against the authors' worst.",
        "- The D1 test set has only 54 images: one mistake = 1.8 percentage points, so do not over-read the",
        "  difference between 0.98 and 1.00.",
        "- The paper reports F1 = 0 for EfficientNet-B0 / B7 / V2-M (everything predicted as the majority class);",
        "  Figure 4 shades these in light red, which must not be read as \"we are better\".",
        "- Figure 3 shows the highest / lowest accuracy run of each dataset; it is **illustrative**, not a random sample.",
        "",
    ]
    (out / "INDEX.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-separated figure numbers, e.g. 1,3; empty = all")
    ap.add_argument("--out", type=Path, default=FIGDIR)
    ap.add_argument("--dpi", type=int, default=200)
    args = ap.parse_args()

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: F811

    globals()["plt"] = plt
    style(plt)
    plt.rcParams["savefig.dpi"] = args.dpi

    rows = read_leaderboard()
    models = [m for m in ORDER if any(r["model"] == m for r in rows)]
    missing = sorted({r["model"] for r in rows} - set(models))
    if missing:
        models += missing

    args.out.mkdir(parents=True, exist_ok=True)
    wanted = {int(x) for x in args.only.split(",") if x.strip()} if args.only else {1, 2, 3, 4, 5}
    jobs = {1: fig_accuracy, 2: fig_heatmap, 3: fig_confusion, 4: fig_delta, 5: fig_ranking}
    made = []
    for no in sorted(wanted):
        if no not in jobs:
            print(f"[figures] skipping unknown figure number {no}")
            continue
        jobs[no](models, rows, args.out)
        name = {1: "fig_accuracy_by_model.png", 2: "fig_optimizer_heatmap.png",
                3: "fig_confusion_grid.png", 4: "fig_delta_acc.png", 5: "fig_ranking.png"}[no]
        made.append(name)
        print(f"[figures] {no} -> {name}", flush=True)

    write_index(args.out, made)
    print(f"[figures] {len(made)} figures + INDEX.md → {args.out}")


if __name__ == "__main__":
    main()
