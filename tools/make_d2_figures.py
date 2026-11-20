"""D2-primary charts: the deck reports accuracy on D2 (603 test images) by default.

D1 has only 54 test images and 18 of 33 runs sit exactly at 1.0000, which reads as
suspicious; D2 has 603 test images, one perfect run, and a real 8-point spread.

Adds:
    slide_backbones_d2.png   backbones sorted by D2, D1 shown as reference dots
    slide_tuning_d2.png      optimiser spread and epoch curves, all on D2
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "assets"

INK, MUTED, ACCENT, ACCENT_2, GREEN, AMBER = "#12263A", "#5F7488", "#0E8FB6", "#7CC6DE", "#12855A", "#B45309"
plt.rcParams.update({
    "font.family": "Segoe UI", "font.size": 15, "axes.titlesize": 17, "axes.labelsize": 15,
    "xtick.labelsize": 13, "ytick.labelsize": 13, "legend.fontsize": 13,
    "axes.edgecolor": "#C9D6E2", "figure.facecolor": "white", "savefig.facecolor": "white",
})
SHORT = {
    "vgg16": "VGG16", "vgg19": "VGG19", "resnet50": "ResNet50", "resnet101": "ResNet101",
    "mobilenet_v2": "MobileNetV2", "xception": "Xception",
    "inception_resnet_v2": "InceptionResNetV2", "nasnet_large": "NASNetLarge",
    "efficientnet_b0": "EffNet-B0", "efficientnet_b7": "EffNet-B7", "efficientnet_v2m": "EffNet-V2M",
}


def _trim(path: Path, pad: int = 8) -> None:
    from PIL import Image, ImageChops

    with Image.open(path) as im:
        rgb = im.convert("RGB")
        bbox = ImageChops.difference(rgb, Image.new("RGB", rgb.size, (255, 255, 255))).getbbox()
        if bbox:
            left, top, right, bottom = bbox
            rgb.crop((max(0, left - pad), max(0, top - pad),
                      min(rgb.width, right + pad), min(rgb.height, bottom + pad))).save(path)


def _save(fig, name: str) -> None:
    path = OUT / name
    fig.savefig(path, dpi=150, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    _trim(path)
    print(f"[d2] {name:26s} {path.stat().st_size / 1024:6.0f} KB")


def _means() -> dict[str, dict[str, float]]:
    rows = [r for r in csv.DictReader((ROOT / "results" / "leaderboard.csv").open(encoding="utf-8"))
            if r.get("accuracy")]
    bucket: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        bucket[r["model"]][r["dataset"]].append(float(r["accuracy"]))
    return {m: {ds: sum(v) / len(v) for ds, v in per.items()} for m, per in bucket.items()}


def backbones_d2() -> None:
    means = _means()
    models = sorted(means, key=lambda m: -means[m]["D2"])
    d2 = [means[m]["D2"] for m in models]
    d1 = [means[m]["D1"] for m in models]

    fig, ax = plt.subplots(figsize=(13.2, 6.0))
    y = np.arange(len(models))
    ax.barh(y, d2, height=0.58, color=ACCENT, label="D2 — 603 test images (reported)")
    ax.scatter(d1, y, s=46, color=MUTED, zorder=3, label="D1 — 54 test images (reference)")
    for yi, value in zip(y, d2):
        ax.text(value + 0.0015, yi, f"{value:.3f}", va="center", fontsize=12.5, color=INK,
                fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([SHORT[m] for m in models], fontsize=13)
    ax.invert_yaxis()
    ax.set_xlim(0.90, 1.012)
    ax.set_xlabel("mean test accuracy over the three optimisers (D2)")
    ax.axvline(1.0, color=MUTED, lw=1.0, ls=":")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    _save(fig, "slide_backbones_d2.png")


def tuning_d2() -> None:
    runs = ROOT / "results" / "runs"
    backbones = ["vgg16", "mobilenet_v2", "efficientnet_v2m"]
    pretty = ["VGG16", "MobileNetV2", "EffNet-V2M"]
    optimisers = ["adam", "sgd", "rmsprop"]
    opt_labels = ["Adam", "SGD", "RMSprop"]
    colours = [ACCENT, MUTED, ACCENT_2]
    width = 0.26

    fig, axes = plt.subplots(1, 2, figsize=(14.4, 5.2), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axes[0]
    xs = np.arange(len(backbones))
    for k, (opt, label, colour) in enumerate(zip(optimisers, opt_labels, colours)):
        vals = []
        for bb in backbones:
            import json
            metrics = json.loads((runs / f"{bb}__D2__{opt}__s42" / "metrics.json").read_text(encoding="utf-8"))
            vals.append(float(metrics["metrics"]["test"]["accuracy"]))
        ax.bar(xs + (k - 1) * width, vals, width, color=colour, label=label)
        for x, v in zip(xs + (k - 1) * width, vals):
            ax.text(x, v + 0.004, f"{v:.3f}", ha="center", fontsize=9.5, color=INK)
    ax.set_xticks(xs)
    ax.set_xticklabels(pretty, fontsize=12.5)
    ax.set_ylim(0.88, 1.015)
    ax.set_ylabel("D2 test accuracy")
    ax.set_title("same data, different settings", fontsize=16, color=INK, fontweight="bold")
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.16), fontsize=11)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    ax = axes[1]
    for opt, label, colour in zip(optimisers, opt_labels, colours):
        rows = list(csv.DictReader((runs / f"efficientnet_v2m__D2__{opt}__s42" / "train_log.csv")
                                   .open(encoding="utf-8")))
        ax.plot([int(r["epoch"]) for r in rows], [float(r["val_acc"]) for r in rows],
                color=colour, linewidth=2.2, label=label)
    ax.set_xlabel("epoch")
    ax.set_ylabel("validation accuracy")
    ax.set_ylim(0.86, 1.005)
    ax.set_title("EffNet-V2M on D2, epoch by epoch", fontsize=16, color=INK, fontweight="bold")
    ax.legend(frameon=False, loc="lower right")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    _save(fig, "slide_tuning_d2.png")


if __name__ == "__main__":
    backbones_d2()
    tuning_d2()
