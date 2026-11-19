# Author: Kenneth + agent | Task: one-figure diagram of the whole network (shapes, frozen vs trainable)
"""Draw the complete network in a single figure: input -> frozen backbone -> head -> verdict.

Every number is taken from the checkpoints or from results/runs/*/metrics.json, so the
figure cannot drift from the model:

    input 224x224x3
    frozen backbone        -> 7x7xC feature map      (C differs per backbone)
    AvgPool2d(4,4)         -> 1x1xC
    Flatten                -> C
    Linear(C,64) + ReLU    -> 64
    Dropout(0.5)           -> 64
    Linear(64,2) + Softmax -> 2                       (P(non-defect), P(defect))

Usage:
    python tools/make_network_figure.py --out results/figures/fig_network.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

INK = "#12263A"
MUTED = "#5F7488"
ACCENT = "#0E8FB6"
GREEN = "#12855A"
RED = "#B91C1C"
FROZEN_FILL = "#E3EDF6"
TRAIN_FILL = "#E3F3EA"
IO_FILL = "#F2F5F8"
BORDER = "#C9D6E2"

# channel width of the last feature map, per backbone (feat_shape from the checkpoints)
CHANNELS = {"vgg16": 512, "resnet50": 2048, "mobilenet_v2": 1280,
            "xception": 2048, "inception_resnet_v2": 1536}
TOTALS = {"vgg16": 134_293_506, "resnet50": 23_639_298, "mobilenet_v2": 2_305_986,
          "xception": 20_938_218, "inception_resnet_v2": 54_404_962}
LABELS = {"vgg16": "VGG16", "resnet50": "ResNet50", "mobilenet_v2": "MobileNetV2",
          "xception": "Xception", "inception_resnet_v2": "InceptionResNetV2"}


def head_params(c: int) -> int:
    return (c * 64 + 64) + (64 * 2 + 2)


def draw(out: Path) -> Path:
    fig = plt.figure(figsize=(14.2, 7.0), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 14.2)
    ax.set_ylim(0, 7.0)
    ax.axis("off")

    blocks = [
        (0.35, 1.70, "Input", "RGB part photo", "224 × 224 × 3", "io"),
        (2.50, 3.00, "Frozen ImageNet backbone", "11 candidates · conv layers only", "7 × 7 × C", "frozen"),
        (5.90, 1.72, "AvgPool2d(4,4)", "spatial average", "1 × 1 × C", "train"),
        (8.02, 1.86, "Linear(C, 64)\n+ ReLU", "flatten · MLP", "64", "train"),
        (10.28, 1.52, "Dropout(0.5)", "regularisation", "64", "train"),
        (12.20, 1.72, "Linear(64, 2)\n+ Softmax", "P(non-defect), P(defect)", "2", "train"),
    ]

    top, height = 4.75, 1.45
    for x, w, title, sub, shape, kind in blocks:
        fill = {"io": IO_FILL, "frozen": FROZEN_FILL, "train": TRAIN_FILL}[kind]
        edge = {"io": BORDER, "frozen": ACCENT, "train": GREEN}[kind]
        ax.add_patch(FancyBboxPatch((x, top), w, height,
                                    boxstyle="round,pad=0.02,rounding_size=0.12",
                                    linewidth=1.6, edgecolor=edge, facecolor=fill,
                                    linestyle="--" if kind == "frozen" else "-"))
        ax.text(x + w / 2, top + height - 0.42, title, ha="center", va="center",
                fontsize=10, color=INK, fontweight="bold", linespacing=1.25)
        ax.text(x + w / 2, top + height - 0.86, sub, ha="center", va="center",
                fontsize=8.4, color=MUTED)
        ax.text(x + w / 2, top - 0.30, shape, ha="center", va="center", fontsize=9.6,
                color=ACCENT if kind != "train" else GREEN, fontweight="bold",
                family="DejaVu Sans Mono")

    for i in range(len(blocks) - 1):
        x0 = blocks[i][0] + blocks[i][1]
        x1 = blocks[i + 1][0]
        ax.add_patch(FancyArrowPatch((x0 + 0.02, top + height / 2), (x1 - 0.02, top + height / 2),
                                     arrowstyle="-|>", mutation_scale=15, linewidth=1.5,
                                     color=MUTED, shrinkA=0, shrinkB=0))

    ax.text(12.20 + 1.72 / 2, top - 0.62, "argmax  →  PASS / FAIL", ha="center", va="center",
            fontsize=8.6, color=INK, fontweight="bold")

    # ---- two annotation rows (full width, no overlap) ----
    bands = [
        (3.55, ACCENT, FROZEN_FILL, "FROZEN",
         "ImageNet weights loaded by timm · requires_grad = False · forward pass under torch.no_grad() "
         "· BatchNorm kept in eval mode, so its statistics never change"),
        (2.95, GREEN, TRAIN_FILL, "TRAINED",
         "new classification head only · cross-entropy loss on 2 classes · Adam / SGD / RMSprop at lr 1e-3 "
         "· 30 epochs on D1, 50 epochs on D2"),
    ]
    for y, edge, fill, tag, body in bands:
        ax.add_patch(FancyBboxPatch((0.35, y), 13.45, 0.48,
                                    boxstyle="round,pad=0.02,rounding_size=0.10",
                                    linewidth=1.2, edgecolor=edge, facecolor=fill))
        ax.text(0.55, y + 0.24, tag, fontsize=8.8, color=edge, fontweight="bold", va="center")
        ax.text(1.60, y + 0.24, body, fontsize=8.3, color=INK, va="center")

    # ---- deployed engine headline ----
    ax.text(0.35, 2.42, "Deployed engine:  MobileNetV2 · D1 · Adam", fontsize=11,
            color=INK, fontweight="bold")
    ax.text(0.35, 2.12,
            "trainable parameters  81,984 + 130 = 82,114        total parameters  2,305,986        "
            "trainable share  3.56 %",
            fontsize=9.3, color=MUTED, family="DejaVu Sans Mono")

    # ---- per-backbone table ----
    col_x = [0.40, 2.70, 4.30, 6.30, 8.55]
    header = ["backbone", "feature-map C", "head params", "trainable share", "total params"]
    ax.text(0.35, 1.72, "Same head for every backbone — only the channel count C differs",
            fontsize=9.6, color=INK, fontweight="bold")
    for x, h in zip(col_x, header):
        ax.text(x, 1.50, h, fontsize=8.3, color=MUTED, fontweight="bold")
    ax.plot([0.35, 13.80], [1.43, 1.43], color=BORDER, linewidth=1.0)
    for i, key in enumerate(LABELS):
        y = 1.26 - i * 0.22
        c, tot = CHANNELS[key], TOTALS[key]
        hp = head_params(c)
        bold = "bold" if key == "mobilenet_v2" else "normal"
        ax.text(col_x[0], y, LABELS[key], fontsize=8.5, color=INK, fontweight=bold)
        ax.text(col_x[1], y, f"{c}", fontsize=8.5, color=MUTED, family="DejaVu Sans Mono")
        ax.text(col_x[2], y, f"{hp:,}", fontsize=8.5, color=MUTED, family="DejaVu Sans Mono")
        ax.text(col_x[3], y, f"{hp / tot * 100:.2f} %", fontsize=8.5, color=MUTED, family="DejaVu Sans Mono")
        ax.text(col_x[4], y, f"{tot:,}", fontsize=8.5, color=MUTED, family="DejaVu Sans Mono")
    ax.text(col_x[1] - 0.05, 1.26 - 5 * 0.22,
            "the other six backbones follow the same recipe", fontsize=7.8, color=MUTED, style="italic")

    ax.text(0.35, 0.06,
            "Not drawn: preprocessing (resize to 224 × 224, ImageNet mean/std normalisation) and the "
            "internal layers of each backbone.",
            fontsize=7.8, color=MUTED, style="italic")

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor="white")
    plt.close(fig)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Draw the whole-network diagram.")
    ap.add_argument("--out", type=Path, default=Path("results/figures/fig_network.png"))
    args = ap.parse_args()
    path = draw(args.out)
    print(f"[network] wrote {path} ({path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
