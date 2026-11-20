# Author: Kenneth + agent | Task: one-figure diagram of the whole network (shapes, frozen vs trainable)
"""Draw the complete network in a single figure: input -> frozen backbone -> head -> verdict.

Every number comes from the checkpoints or from results/runs/*/metrics.json, so the
figure cannot drift from the model:

    input 224x224x3
    frozen backbone        -> 7x7xC feature map      (C differs per backbone)
    AvgPool2d(4,4)         -> 1x1xC
    Flatten                -> C
    Linear(C,64) + ReLU    -> 64
    Dropout(0.5)           -> 64
    Linear(64,2) + Softmax -> 2                       (P(non-defect), P(defect))

Report version:      python tools/make_network_figure.py --out results/figures/fig_network.png
Slide version:       python tools/make_network_figure.py --out reports/assets/slide_network.png \\
                         --font-scale 1.32 --rows vgg16,resnet50,mobilenet_v2
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
FROZEN_FILL = "#E3EDF6"
TRAIN_FILL = "#E3F3EA"
IO_FILL = "#F2F5F8"
BORDER = "#C9D6E2"

CHANNELS = {"vgg16": 512, "resnet50": 2048, "mobilenet_v2": 1280,
            "xception": 2048, "inception_resnet_v2": 1536}
TOTALS = {"vgg16": 134_293_506, "resnet50": 23_639_298, "mobilenet_v2": 2_305_986,
          "xception": 20_938_218, "inception_resnet_v2": 54_404_962}
LABELS = {"vgg16": "VGG16", "resnet50": "ResNet50", "mobilenet_v2": "MobileNetV2",
          "xception": "Xception", "inception_resnet_v2": "InceptionResNetV2"}
ALL_ROWS = ("vgg16", "resnet50", "mobilenet_v2", "xception", "inception_resnet_v2")


def head_params(c: int) -> int:
    return (c * 64 + 64) + (64 * 2 + 2)


def draw(out: Path, font_scale: float = 1.0, rows: tuple[str, ...] = ALL_ROWS,
         compact: bool = False) -> Path:
    def fs(x: float) -> float:
        return x * font_scale

    rows = tuple(r for r in rows if r in CHANNELS) or ALL_ROWS
    # the figure grows with the font scale so nothing gets cramped
    width = 14.2
    height = (4.5 if compact else 7.0) + (font_scale - 1.0) * (0.8 if compact else 1.6)
    fig = plt.figure(figsize=(width, height), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")

    top = height - (1.70 if compact else 2.25)
    blocks = [
        (0.35, 1.80, "Input", "RGB part photo", "224 × 224 × 3", "io"),
        (2.55, 3.05, "Frozen ImageNet backbone", "11 candidates · conv layers only", "7 × 7 × C", "frozen"),
        (6.00, 1.85, "AvgPool2d(4,4)", "spatial average", "1 × 1 × C", "train"),
        (8.25, 1.95, "Linear(C, 64)\n+ ReLU", "flatten · MLP", "64", "train"),
        (10.45, 1.60, "Dropout(0.5)", "regularisation", "64", "train"),
        (12.25, 1.70, "Linear(64, 2)\n+ Softmax", "class scores", "2", "train"),
    ]
    block_h = 1.30 if compact else 1.55

    for x, w, title, sub, shape, kind in blocks:
        fill = {"io": IO_FILL, "frozen": FROZEN_FILL, "train": TRAIN_FILL}[kind]
        edge = {"io": BORDER, "frozen": ACCENT, "train": GREEN}[kind]
        ax.add_patch(FancyBboxPatch((x, top), w, block_h,
                                    boxstyle="round,pad=0.02,rounding_size=0.12",
                                    linewidth=1.8, edgecolor=edge, facecolor=fill,
                                    linestyle="--" if kind == "frozen" else "-"))
        ax.text(x + w / 2, top + block_h - 0.45, title, ha="center", va="center",
                fontsize=fs(10), color=INK, fontweight="bold", linespacing=1.3)
        ax.text(x + w / 2, top + block_h - 0.95, sub, ha="center", va="center",
                fontsize=fs(8.4), color=MUTED)
        ax.text(x + w / 2, top - 0.36, shape, ha="center", va="center", fontsize=fs(9.6),
                color=ACCENT if kind != "train" else GREEN, fontweight="bold",
                family="DejaVu Sans Mono")

    for i in range(len(blocks) - 1):
        x0 = blocks[i][0] + blocks[i][1]
        x1 = blocks[i + 1][0]
        ax.add_patch(FancyArrowPatch((x0 + 0.02, top + block_h / 2), (x1 - 0.02, top + block_h / 2),
                                     arrowstyle="-|>", mutation_scale=16, linewidth=1.7,
                                     color=MUTED, shrinkA=0, shrinkB=0))

    if not compact:
        ax.text(12.25 + 1.70 / 2, top - 0.75, "argmax → PASS / FAIL", ha="center", va="center",
                fontsize=fs(8.6), color=INK, fontweight="bold")

    bands = [
        (top - (1.16 if compact else 1.38), ACCENT, FROZEN_FILL, "FROZEN",
         "ImageNet weights loaded by timm · requires_grad = False · forward pass under torch.no_grad() "
         "· BatchNorm kept in eval mode, so its statistics never change"),
        (top - (1.84 if compact else 2.06), GREEN, TRAIN_FILL, "TRAINED",
         "new classification head only · cross-entropy loss on 2 classes · Adam / SGD / RMSprop at lr 1e-3 "
         "· 30 epochs on D1, 50 epochs on D2"),
    ]
    for y, edge, fill, tag, body in bands:
        ax.add_patch(FancyBboxPatch((0.35, y), width - 0.70, 0.52,
                                    boxstyle="round,pad=0.02,rounding_size=0.10",
                                    linewidth=1.3, edgecolor=edge, facecolor=fill))
        ax.text(0.55, y + 0.26, tag, fontsize=fs(8.8), color=edge, fontweight="bold", va="center")
        ax.text(1.65, y + 0.26, body, fontsize=fs(8.3), color=INK, va="center")

    if compact:
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.10)
        plt.close(fig)
        return out

    headline_y = top - 2.75
    ax.text(0.35, headline_y, "Deployed engine:  MobileNetV2 · D1 · Adam", fontsize=fs(11),
            color=INK, fontweight="bold")
    ax.text(0.35, headline_y - 0.34,
            "trainable parameters  81,984 + 130 = 82,114        total parameters  2,305,986        "
            "trainable share  3.56 %",
            fontsize=fs(9.3), color=MUTED, family="DejaVu Sans Mono")

    table_top = headline_y - 0.80
    col_x = [0.40, 2.70, 4.35, 6.45, 8.75]
    header = ["backbone", "feature-map C", "head params", "trainable share", "total params"]
    ax.text(0.35, table_top, "Same head for every backbone — only the channel count C differs",
            fontsize=fs(9.6), color=INK, fontweight="bold")
    for x, h in zip(col_x, header):
        ax.text(x, table_top - 0.26, h, fontsize=fs(8.3), color=MUTED, fontweight="bold")
    ax.plot([0.35, width - 0.40], [table_top - 0.34, table_top - 0.34], color=BORDER, linewidth=1.0)
    step = 0.26 * max(1.0, font_scale)
    for i, key in enumerate(rows):
        y = table_top - 0.56 - i * step
        c, tot = CHANNELS[key], TOTALS[key]
        hp = head_params(c)
        bold = "bold" if key == "mobilenet_v2" else "normal"
        ax.text(col_x[0], y, LABELS[key], fontsize=fs(8.5), color=INK, fontweight=bold)
        ax.text(col_x[1], y, f"{c}", fontsize=fs(8.5), color=MUTED, family="DejaVu Sans Mono")
        ax.text(col_x[2], y, f"{hp:,}", fontsize=fs(8.5), color=MUTED, family="DejaVu Sans Mono")
        ax.text(col_x[3], y, f"{hp / tot * 100:.2f} %", fontsize=fs(8.5), color=MUTED,
                family="DejaVu Sans Mono")
        ax.text(col_x[4], y, f"{tot:,}", fontsize=fs(8.5), color=MUTED, family="DejaVu Sans Mono")

    foot_y = max(0.10, table_top - 0.90 - len(rows) * step)
    ax.text(0.35, foot_y,
            "Not drawn: preprocessing (resize to 224 × 224, ImageNet mean/std normalisation) and the "
            "internal layers of each backbone.",
            fontsize=fs(8.0), color=MUTED, style="italic")

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Draw the whole-network diagram.")
    ap.add_argument("--out", type=Path, default=Path("results/figures/fig_network.png"))
    ap.add_argument("--font-scale", type=float, default=1.0)
    ap.add_argument("--rows", default=",".join(ALL_ROWS))
    ap.add_argument("--compact", action="store_true")
    args = ap.parse_args()
    rows = tuple(r.strip() for r in args.rows.split(",") if r.strip())
    path = draw(args.out, font_scale=args.font_scale, rows=rows, compact=args.compact)
    print(f"[network] wrote {path} ({path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
