# Author: Kenneth + agent | Task: extra slide-only figures (more visuals for the deck)
"""Extra figures used only by the slides: sample grid, data split, pipeline, timeline,
pseudocode card, tuning evidence and confusion matrices.

All numbers come from the repository (splits/*.csv, results/runs/*/metrics.json,
results/runs/*/train_log.csv, testset/). Report figures in results/figures/ are untouched.

Usage:
    python tools/make_slide_extras.py            # all
    python tools/make_slide_extras.py --only grid,split,tuning
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "reports" / "assets"
TESTSET = ROOT / "testset"
RUNS = ROOT / "results" / "runs"

INK = "#12263A"
MUTED = "#5F7488"
ACCENT = "#0E8FB6"
ACCENT_2 = "#7CC6DE"
GREEN = "#12855A"
AMBER = "#B45309"
RED = "#B91C1C"
CARD = "#F5F8FB"
BORDER = "#C9D6E2"

plt.rcParams.update({
    "font.family": "Segoe UI",
    "font.size": 15,
    "axes.titlesize": 17,
    "axes.labelsize": 15,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "legend.fontsize": 13,
    "axes.edgecolor": BORDER,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def _save(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=150, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    _trim(path)
    print(f"[extra] {name:28s} {path.stat().st_size / 1024:6.0f} KB")


def _trim(path: Path, pad: int = 8) -> None:
    """Crop the uniform white border that bbox_inches leaves around an axes."""
    from PIL import Image, ImageChops

    with Image.open(path) as im:
        rgb = im.convert("RGB")
        bbox = ImageChops.difference(rgb, Image.new("RGB", rgb.size, (255, 255, 255))).getbbox()
        if not bbox:
            return
        l, t_, r, b = bbox
        rgb.crop((max(0, l - pad), max(0, t_ - pad),
                  min(rgb.width, r + pad), min(rgb.height, b + pad))).save(path)


# ---------------------------------------------------------------- 1. sample grid
def grid() -> None:
    from PIL import Image

    defect_dir = TESTSET / "D1" / "test" / "defect"
    normal_dir = TESTSET / "D1" / "test" / "nondefect"
    rows = 2
    cols = 8
    fig, axes = plt.subplots(rows, cols, figsize=(15.0, 4.9))
    for r, (folder, title, colour) in enumerate(((defect_dir, "DEFECT", RED),
                                                (normal_dir, "NO DEFECT", GREEN))):
        files = sorted(folder.glob("*"))[:cols]
        for c in range(cols):
            ax = axes[r][c]
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            if c < len(files):
                im = Image.open(files[c])
                im.draft("RGB", (400, 400))
                ax.imshow(im.convert("RGB").resize((260, 260)))
            if c == 0:
                ax.set_ylabel(title, fontsize=17, color=colour, fontweight="bold", labelpad=12)
    fig.tight_layout()
    _save(fig, "slide_dataset_grid.png")


# ---------------------------------------------------------------- 2. data split
def split_bars() -> None:
    counts = {"D1": (189, 28, 54), "D2": (2112, 302, 603)}
    fig, ax = plt.subplots(figsize=(13.0, 2.5))
    colours = [ACCENT, ACCENT_2, MUTED]
    names = ["train", "val", "test"]
    for row, (ds, parts) in enumerate(counts.items()):
        total = sum(parts)
        left = 0.0
        for value, colour, name in zip(parts, colours, names):
            pct = value / total * 100
            ax.barh(row, pct, left=left, color=colour, height=0.5,
                    label=name if row == 0 else None)
            ax.text(left + pct / 2, row, f"{value}\n({pct:.0f}%)",
                    ha="center", va="center", fontsize=12, color="white", fontweight="bold")
            left += pct
        ax.text(-2, row, ds, ha="right", va="center", fontsize=16, color=INK, fontweight="bold")
    ax.set_yticks([])
    ax.set_xlim(0, 100)
    ax.set_xlabel("share of the dataset (%)")
    ax.legend(frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.02))
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    _save(fig, "slide_split.png")


# ---------------------------------------------------------------- 3. preprocessing pipeline
def pipeline() -> None:
    fig, ax = plt.subplots(figsize=(14.2, 2.6))
    ax.set_xlim(0, 14.2)
    ax.set_ylim(0.3, 3.0)
    ax.axis("off")
    steps = [
        ("raw photo", "5184 × 3456", "dark"),
        ("resize", "224 × 224", "accent"),
        ("normalise", "ImageNet mean/std", "accent"),
        ("cache", "224 JPEG", "accent"),
        ("stratified split", "70 / 10 / 20 · seed 42", "green"),
    ]
    n = len(steps)
    gap = 0.28
    w = (14.2 - 0.8 - (n - 1) * gap) / n
    palette = {"dark": "#14304C", "accent": ACCENT, "green": GREEN}
    y, h = 1.35, 1.15
    for i, (head, sub, kind) in enumerate(steps):
        x = 0.4 + i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.10",
                                    linewidth=1.6, edgecolor=palette[kind],
                                    facecolor=palette[kind] if kind == "dark" else "white"))
        text_colour = "white" if kind == "dark" else INK
        ax.text(x + w / 2, y + h - 0.36, head, ha="center", va="center", fontsize=12.5,
                color=text_colour, fontweight="bold")
        ax.text(x + w / 2, y + h - 0.76, sub, ha="center", va="center", fontsize=10.5,
                color="white" if kind == "dark" else MUTED)
        if i < n - 1:
            ax.add_patch(FancyArrowPatch((x + w + 0.03, y + h / 2), (x + w + gap - 0.03, y + h / 2),
                                         arrowstyle="-|>", mutation_scale=15, linewidth=1.6,
                                         color=MUTED))
    ax.text(0.4, 0.55, "one cache build ≈ 5 minutes for 3,017 images   ·   one training run then takes "
                       "under a minute on a T4", fontsize=11, color=MUTED)
    _save(fig, "slide_pipeline.png")


# ---------------------------------------------------------------- 4. timeline
def timeline() -> None:
    milestones = [
        ("data + code", 0.0, 1.4, ACCENT),
        ("66 runs", 1.4, 1.6, ACCENT),
        ("figure 1 + tables", 3.0, 1.2, ACCENT_2),
        ("analyses", 4.2, 1.4, ACCENT_2),
        ("report + deck", 5.6, 2.0, GREEN),
        ("submit", 7.6, 0.5, AMBER),
    ]
    fig, ax = plt.subplots(figsize=(13.6, 2.0))
    for name, start, length, colour in milestones:
        ax.barh(0, length, left=start, height=0.42, color=colour)
        ax.text(start + length / 2, 0, name, ha="center", va="center", fontsize=12,
                color="white" if colour != ACCENT_2 else INK, fontweight="bold")
    ax.set_yticks([])
    ax.set_xlim(0, 8.4)
    ax.set_ylim(-0.45, 0.45)
    ax.set_xticks([0, 1.4, 3.0, 4.2, 5.6, 7.6])
    ax.set_xticklabels(["22 Oct", "05 Nov", "12 Nov", "16 Nov", "20 Nov", "30 Nov"])
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    _save(fig, "slide_timeline.png")


# ---------------------------------------------------------------- 5. pseudocode card
def algorithm() -> None:
    lines = [
        ("ALGORITHM 1", "one training run with a frozen backbone"),
        ("Input:", "frozen split file, backbone B, optimiser O, epochs E"),
        ("1", "load B with ImageNet weights;  for p in B.params: p.requires_grad ← False"),
        ("2", "H ← new head:  AvgPool(4) → Flatten → Linear(C,64)+ReLU → Dropout(0.5) → Linear(64,2)"),
        ("3", "for epoch in 1..E:"),
        ("4", "    for (x, y) in train_loader:"),
        ("5", "        f ← B.forward_features(x)          # no_grad, BatchNorm in eval"),
        ("6", "        p ← softmax(H(pool(f)))            # only H is trained"),
        ("7", "        L ← cross_entropy(p, y);  O.step(∇L · H)"),
        ("8", "    record train / val loss and accuracy"),
        ("9", "predict on test split → accuracy, precision, recall, F1, MCC, kappa, AUC, mAP, "
              "sens., spec."),
        ("10", "store metrics.json, curves, confusion matrix, head weights"),
    ]
    fig, ax = plt.subplots(figsize=(12.6, 6.2))
    ax.set_xlim(0, 12.6)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.15, 0.15), 12.3, 5.9, boxstyle="round,pad=0.02,rounding_size=0.12",
                                linewidth=1.4, edgecolor=BORDER, facecolor=CARD))
    y = 5.55
    ax.text(0.55, y, lines[0][0], fontsize=15, color=ACCENT, fontweight="bold", family="DejaVu Sans Mono")
    ax.text(2.85, y, "— " + lines[0][1], fontsize=11.5, color=MUTED, family="DejaVu Sans Mono")
    y -= 0.62
    for tag, body in lines[1:]:
        colour = AMBER if tag == "Input:" else MUTED
        ax.text(0.55, y, tag, fontsize=11.5, color=colour, fontweight="bold", family="DejaVu Sans Mono")
        ax.text(2.05, y, body, fontsize=11.5, color=INK, family="DejaVu Sans Mono")
        y -= 0.44
    _save(fig, "slide_algorithm.png")


# ---------------------------------------------------------------- 6. tuning evidence
def tuning() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14.0, 5.4), gridspec_kw={"width_ratios": [1, 1.25]})

    # left: three backbones x three optimisers (D1 test accuracy)
    backbones = ["vgg16", "mobilenet_v2", "nasnet_large"]
    pretty = ["VGG16", "MobileNetV2", "NASNetLarge"]
    optimisers = ["adam", "sgd", "rmsprop"]
    opt_labels = ["Adam", "SGD", "RMSprop"]
    colours = [ACCENT, MUTED, ACCENT_2]
    width = 0.26
    ax = axes[0]
    xs = np.arange(len(backbones))
    for k, (opt, label, colour) in enumerate(zip(optimisers, opt_labels, colours)):
        vals = []
        for bb in backbones:
            metrics = json.loads((RUNS / f"{bb}__D1__{opt}__s42" / "metrics.json").read_text(encoding="utf-8"))
            vals.append(float(metrics["metrics"]["test"]["accuracy"]))
        ax.bar(xs + (k - 1) * width, vals, width, color=colour, label=label)
        for x, v in zip(xs + (k - 1) * width, vals):
            ax.text(x, v + 0.003, f"{v:.3f}", ha="center", fontsize=9.5, color=INK)
    ax.set_xticks(xs)
    ax.set_xticklabels(pretty, fontsize=12)
    ax.set_ylim(0.86, 1.012)
    ax.set_ylabel("D1 test accuracy")
    ax.set_title("same data, different settings", fontsize=16, color=INK, fontweight="bold")
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.16), fontsize=11)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    # right: validation curves for the weakest backbone (where tuning visibly matters)
    ax = axes[1]
    colours = [ACCENT, MUTED, ACCENT_2]
    for opt, label, colour in zip(optimisers, opt_labels, colours):
        rid = f"nasnet_large__D1__{opt}__s42"
        rows = list(csv.DictReader((RUNS / rid / "train_log.csv").open(encoding="utf-8")))
        epochs = [int(r["epoch"]) for r in rows]
        vals = [float(r["val_acc"]) for r in rows]
        ax.plot(epochs, vals, color=colour, linewidth=2.2, label=label)
    ax.set_xlabel("epoch")
    ax.set_ylabel("validation accuracy")
    ax.set_ylim(0.76, 1.005)
    ax.set_title("NASNetLarge, epoch by epoch", fontsize=16, color=INK, fontweight="bold")
    ax.legend(frameon=False, loc="lower right")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    _save(fig, "slide_tuning.png")


# ---------------------------------------------------------------- 7. confusion matrices
def confusion() -> None:
    picks = [
        ("mobilenet_v2__D1__adam__s42", "MobileNetV2 · D1"),
        ("vgg16__D1__adam__s42", "VGG16 · D1"),
        ("mobilenet_v2__D2__adam__s42", "MobileNetV2 · D2"),
        ("nasnet_large__D1__adam__s42", "NASNetLarge · D1"),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(15.0, 4.2))
    for ax, (rid, label) in zip(axes, picks):
        metrics = json.loads((RUNS / rid / "metrics.json").read_text(encoding="utf-8"))
        cm = np.array(metrics["confusion"]["test"], dtype=int)
        acc = float(metrics["metrics"]["test"]["accuracy"])
        ax.imshow(cm, cmap="Blues", vmin=0, vmax=max(cm.max(), 1))
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["pred ok", "pred defect"], fontsize=11)
        ax.set_yticklabels(["ok", "defect"], fontsize=11)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(cm[i][j]), ha="center", va="center", fontsize=17,
                        color="white" if cm[i][j] > cm.max() * 0.5 else INK, fontweight="bold")
        ax.set_title(f"{label}\nacc {acc:.3f}", fontsize=13, color=INK, fontweight="bold")
    fig.tight_layout()
    _save(fig, "slide_confusion.png")


TASKS = {
    "grid": grid,
    "split": split_bars,
    "pipeline": pipeline,
    "timeline": timeline,
    "algorithm": algorithm,
    "tuning": tuning,
    "confusion": confusion,
}


def main() -> None:
    ap = argparse.ArgumentParser(description="Render the extra slide figures.")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    names = [n.strip() for n in args.only.split(",") if n.strip()] or list(TASKS)
    for name in names:
        fn = TASKS.get(name)
        if fn is None:
            raise SystemExit(f"unknown asset {name}; available: {list(TASKS)}")
        print(f"\n== {name} ==")
        fn()


if __name__ == "__main__":
    main()
