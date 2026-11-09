# Author: Kenneth | Task: Figure 1 - transfer-learning pipeline diagram
"""Generate Figure 1: transfer-learning pipeline and the 66-run experiment matrix.

Output: results/figures/fig_pipeline.png (200 dpi)

Usage:
    python tools/make_pipeline_figure.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

STAGES = [
    ("Dataset", "D1: 271 real images\nD2: 3,017 augmented\n(defect / non-defect)"),
    ("Pre-processing", "resize to 224 x 224\nImageNet normalisation\n(image cache)"),
    ("Frozen backbone", "11 ImageNet CNNs\nVGG16/19, ResNet50/101,\nInceptionResNetV2, Xception,\nMobileNetV2, EffNet-B0/B7/V2-M,\nNASNet-Large"),
    ("Trainable head", "AvgPool2d(4,4)\nFlatten\nLinear(64) + ReLU\nDropout(0.5)\nLinear(2)"),
    ("Training", "Adam / SGD / RMSprop\nhead-only, seed 42\n70 / 10 / 20 split"),
    ("Evaluation", "accuracy, precision, recall,\nf1, MCC, kappa, AUC, mAP,\nsensitivity, specificity"),
]

MATRIX = "Experiment matrix:  11 backbones  x  3 optimizers  x  2 datasets  =  66 runs"


def build(out: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(13.5, 5.2))
    ax.set_xlim(0, 13.5)
    ax.set_ylim(0, 5.2)
    ax.axis("off")

    box_w, box_h = 1.95, 1.85
    gap = 0.22
    x = 0.25
    y = 2.75

    colors = ["#E8F1FA", "#E8F1FA", "#FDEBD3", "#E6F4EA", "#E8F1FA", "#F3E8FD"]

    for idx, (title, body) in enumerate(STAGES):
        patch = mpatches.FancyBboxPatch(
            (x, y), box_w, box_h,
            boxstyle="round,pad=0.03,rounding_size=0.08",
            linewidth=1.1, edgecolor="#4A4A4A", facecolor=colors[idx],
        )
        ax.add_patch(patch)
        ax.text(x + box_w / 2, y + box_h - 0.22, f"{idx + 1}. {title}",
                ha="center", va="top", fontsize=9.5, fontweight="bold")
        ax.text(x + box_w / 2, y + box_h - 0.58, body,
                ha="center", va="top", fontsize=7.0, linespacing=1.35)

        if idx < len(STAGES) - 1:
            ax.annotate(
                "", xy=(x + box_w + gap, y + box_h / 2), xytext=(x + box_w, y + box_h / 2),
                arrowprops=dict(arrowstyle="-|>", color="#4A4A4A", linewidth=1.4, shrinkA=0, shrinkB=0),
            )
        x += box_w + gap

    # experiment matrix banner
    banner = mpatches.FancyBboxPatch(
        (1.2, 1.55), 11.1, 0.62,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        linewidth=1.1, edgecolor="#B23A48", facecolor="#FDECEE",
    )
    ax.add_patch(banner)
    ax.text(6.75, 1.86, MATRIX, ha="center", va="center", fontsize=10.0, fontweight="bold", color="#7A2230")

    # frozen / trainable legend
    frozen = mpatches.Patch(facecolor="#FDEBD3", edgecolor="#4A4A4A", label="Frozen (ImageNet weights, not updated)")
    trainable = mpatches.Patch(facecolor="#E6F4EA", edgecolor="#4A4A4A", label="Trainable (new classification head)")
    ax.legend(handles=[frozen, trainable], loc="lower left", fontsize=8.0, frameon=False,
              bbox_to_anchor=(0.04, 0.02))

    ax.text(13.3, 0.18, "Each run reports 10 metrics on train / val / test.",
            ha="right", va="bottom", fontsize=7.5, style="italic", color="#555555")

    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate Figure 1 (pipeline diagram).")
    ap.add_argument("--out", type=Path, default=Path("results/figures/fig_pipeline.png"))
    args = ap.parse_args()
    path = build(args.out)
    print(f"[pipeline] wrote {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
