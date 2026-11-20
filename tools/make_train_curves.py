# Author: Kenneth + agent | Task: training-curve figure for the "how a run trains" slide
"""Plot the train/val loss and accuracy of one real run so the training slide has a picture.

Data: results/runs/<run_id>/train_log.csv (written by src/train.py).

Usage:
    python tools/make_train_curves.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "assets" / "slide_train_curves.png"
RUNS = ROOT / "results" / "runs"

INK, MUTED, ACCENT, ACCENT_2, BORDER = "#12263A", "#5F7488", "#0E8FB6", "#7CC6DE", "#C9D6E2"
plt.rcParams.update({
    "font.family": "Segoe UI", "font.size": 15, "axes.titlesize": 17,
    "axes.labelsize": 15, "xtick.labelsize": 13, "ytick.labelsize": 13, "legend.fontsize": 13,
    "axes.edgecolor": BORDER, "figure.facecolor": "white", "savefig.facecolor": "white",
})


def curves(run_id: str = "mobilenet_v2__D1__adam__s42") -> None:
    rows = list(csv.DictReader((RUNS / run_id / "train_log.csv").open(encoding="utf-8")))
    epochs = [int(r["epoch"]) for r in rows]
    tr_loss = [float(r["train_loss"]) for r in rows]
    va_loss = [float(r["val_loss"]) for r in rows]
    tr_acc = [float(r["train_acc"]) for r in rows]
    va_acc = [float(r["val_acc"]) for r in rows]

    fig, axes = plt.subplots(1, 2, figsize=(14.0, 5.0))
    ax = axes[0]
    ax.plot(epochs, tr_loss, color=ACCENT, linewidth=2.2, label="train")
    ax.plot(epochs, va_loss, color=ACCENT_2, linewidth=2.2, label="validation")
    ax.set_xlabel("epoch")
    ax.set_ylabel("cross-entropy loss")
    ax.set_title("loss", fontsize=16, color=INK, fontweight="bold")
    ax.legend(frameon=False)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    ax = axes[1]
    ax.plot(epochs, tr_acc, color=ACCENT, linewidth=2.2, label="train")
    ax.plot(epochs, va_acc, color=ACCENT_2, linewidth=2.2, label="validation")
    ax.set_xlabel("epoch")
    ax.set_ylabel("accuracy")
    ax.set_ylim(0.75, 1.01)
    ax.set_title("accuracy", fontsize=16, color=INK, fontweight="bold")
    ax.legend(frameon=False, loc="lower right")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print(f"[curves] {OUT.name}  {OUT.stat().st_size / 1024:.0f} KB  ({run_id})")


if __name__ == "__main__":
    curves()
