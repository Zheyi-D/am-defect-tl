# Author: Kenneth + agent | Task: slide-optimised versions of the report figures (bigger fonts)
"""Render the figures that go on the slides, with fonts sized for projection.

The report figures in results/figures/ stay untouched (they are sized for print);
these versions live in reports/assets/ and are used only by tools/build_slides_pptx.py.

Every number comes from the repository:
    results/leaderboard.csv      -> backbone / optimizer / delta charts
    results/leakage.csv          -> leakage control chart
    results/efficiency.csv       -> deployment cost chart
    results/runs/*/model.pt      -> Grad-CAM panels (regenerated so the fonts are large)

Usage:
    python tools/make_slide_figures.py            # all assets
    python tools/make_slide_figures.py --only backbones,delta
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT = ROOT / "reports" / "assets"
FIG = ROOT / "results" / "figures"

INK = "#12263A"
MUTED = "#5F7488"
ACCENT = "#0E8FB6"
ACCENT_2 = "#7CC6DE"
GREEN = "#12855A"
AMBER = "#B45309"
RED = "#B91C1C"
NAVY = "#0B2239"
LIGHT = "#E3EDF6"

# projection-friendly defaults
plt.rcParams.update({
    "font.family": "Segoe UI",
    "font.size": 15,
    "axes.titlesize": 17,
    "axes.labelsize": 15,
    "xtick.labelsize": 13.5,
    "ytick.labelsize": 13.5,
    "legend.fontsize": 13.5,
    "axes.edgecolor": "#C9D6E2",
    "axes.linewidth": 1.0,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})

SHORT = {
    "vgg16": "VGG16", "vgg19": "VGG19", "resnet50": "ResNet50", "resnet101": "ResNet101",
    "mobilenet_v2": "MobileNetV2", "xception": "Xception",
    "inception_resnet_v2": "InceptionResNetV2", "nasnet_large": "NASNetLarge",
    "efficientnet_b0": "EffNet-B0", "efficientnet_b7": "EffNet-B7",
    "efficientnet_v2m": "EffNet-V2M",
}


def _save(fig, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=150, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    print(f"[assets] {name}  {path.stat().st_size / 1024:.0f} KB")
    return path


def _leaderboard() -> list[dict]:
    rows = list(csv.DictReader((ROOT / "results" / "leaderboard.csv").open(encoding="utf-8")))
    return [r for r in rows if r.get("accuracy")]


# ---------------------------------------------------------------- data assets
def assets_samples() -> None:
    from PIL import Image, ImageDraw, ImageFont

    pos = ROOT / "testset" / "D1" / "test" / "defect" / "IMG_9153.jpg"
    neg = ROOT / "testset" / "D1" / "test" / "nondefect" / "IMG_8930.jpg"
    if not (pos.exists() and neg.exists()):
        print("[assets] sample photos missing, skipped")
        return
    size = 760
    panels = []
    for path, label, colour in ((pos, "DEFECT  (stringing)", RED), (neg, "NO DEFECT", GREEN)):
        with Image.open(path) as im:
            im = im.convert("RGB")
            im = im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)
            canvas = Image.new("RGB", (size, im.height + 86), "white")
            canvas.paste(im, (0, 0))
            draw = ImageDraw.Draw(canvas)
            draw.rectangle([0, im.height, size, im.height + 86], fill=colour)
            try:
                font = ImageFont.truetype("segoeuib.ttf", 40)
            except Exception:
                font = ImageFont.load_default()
            draw.text((24, im.height + 22), label, font=font, fill="white")
        panels.append(canvas)
    h = min(p.height for p in panels)
    gap = 26
    out = Image.new("RGB", (size * 2 + gap, h), "white")
    out.paste(panels[0].crop((0, 0, size, h)), (0, 0))
    out.paste(panels[1].crop((0, 0, size, h)), (size + gap, 0))
    path = OUT / "slide_samples.png"
    OUT.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print(f"[assets] slide_samples.png  {path.stat().st_size / 1024:.0f} KB")


def assets_augmentation() -> None:
    from PIL import Image, ImageEnhance

    src = ROOT / "testset" / "D1" / "test" / "defect" / "IMG_9153.jpg"
    if not src.exists():
        return
    im = Image.open(src).convert("RGB")
    w = 620
    im = im.resize((w, int(w * im.height / im.width)), Image.LANCZOS)
    variants = [
        ("original", im, INK),
        ("rotate +15°", im.rotate(15, fillcolor=(20, 20, 20)), ACCENT),
        ("horizontal flip", im.transpose(Image.FLIP_LEFT_RIGHT), ACCENT),
        ("brightness ×1.3", ImageEnhance.Brightness(im).enhance(1.3), ACCENT),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(14.4, 4.6))
    for ax, (label, img, colour) in zip(axes, variants):
        ax.imshow(img)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_title(label, fontsize=17, color=colour, fontweight="bold", pad=10)
    fig.tight_layout()
    _save(fig, "slide_augmentation.png")


# ---------------------------------------------------------------- result assets
def assets_backbones() -> None:
    rows = _leaderboard()
    bucket: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in rows:
        bucket[(r["model"], r["dataset"])].append(float(r["accuracy"]))
    models = sorted({r["model"] for r in rows},
                    key=lambda m: -sum(bucket[(m, "D1")]) / len(bucket[(m, "D1")]))
    d1 = [sum(bucket[(m, "D1")]) / len(bucket[(m, "D1")]) for m in models]
    d2 = [sum(bucket[(m, "D2")]) / len(bucket[(m, "D2")]) for m in models]

    fig, ax = plt.subplots(figsize=(13.2, 6.4))
    y = np.arange(len(models))
    height = 0.38
    ax.barh(y + height / 2, d1, height, color=ACCENT, label="D1 (real photos)")
    ax.barh(y - height / 2, d2, height, color=ACCENT_2, label="D2 (augmented)")
    span = 0.90
    for yi, v in zip(y + height / 2, d1):
        inside = v > span + 0.055
        ax.text(v - (0.004 if inside else -0.004), yi, f"{v:.3f}", va="center",
                ha="right" if inside else "left", fontsize=12.5,
                color="white" if inside else INK, fontweight="bold" if inside else "normal")
    for yi, v in zip(y - height / 2, d2):
        inside = v > span + 0.075
        ax.text(v - (0.004 if inside else -0.004), yi, f"{v:.3f}", va="center",
                ha="right" if inside else "left", fontsize=12.5,
                color="white" if inside else MUTED)
    ax.set_yticks(y)
    ax.set_yticklabels([SHORT[m] for m in models])
    ax.invert_yaxis()
    ax.set_xlim(span, 1.008)
    ax.set_xlabel("mean test accuracy over the three optimizers")
    ax.axvline(1.0, color=MUTED, lw=1.0, ls=":")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    _save(fig, "slide_backbones.png")


def assets_optimizer() -> None:
    rows = _leaderboard()
    models = sorted({r["model"] for r in rows})
    opts = ["adam", "sgd", "rmsprop"]
    fig, axes = plt.subplots(1, 2, figsize=(13.4, 6.2))
    for ax, ds in zip(axes, ("D1", "D2")):
        grid = np.full((len(models), len(opts)), np.nan)
        for r in rows:
            if r["dataset"] != ds:
                continue
            i, j = models.index(r["model"]), opts.index(r["optimizer"])
            grid[i, j] = float(r["accuracy"])
        im = ax.imshow(grid, cmap="YlGn", vmin=0.90, vmax=1.0, aspect="auto")
        ax.set_xticks(range(len(opts)))
        ax.set_xticklabels([o.capitalize() for o in opts], fontsize=14)
        ax.set_yticks(range(len(models)))
        ax.set_yticklabels([SHORT[m] for m in models], fontsize=13)
        ax.set_title(f"{ds} — test accuracy", fontsize=17, color=INK, fontweight="bold", pad=10)
        for i in range(len(models)):
            for j in range(len(opts)):
                if np.isnan(grid[i, j]):
                    continue
                ax.text(j, i, f"{grid[i, j]:.3f}", ha="center", va="center", fontsize=12,
                        color="white" if grid[i, j] > 0.975 else INK, fontweight="bold")
    cbar = fig.colorbar(im, ax=axes, fraction=0.02, pad=0.02)
    cbar.ax.tick_params(labelsize=12)
    _save(fig, "slide_optimizer.png")


def assets_delta() -> None:
    rows = _leaderboard()
    bucket: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    for r in rows:
        if not r.get("paper_acc"):
            continue
        bucket[(r["model"], r["dataset"])].append((float(r["accuracy"]), float(r["paper_acc"])))
    fig, axes = plt.subplots(1, 2, figsize=(13.4, 5.8))
    for ax, ds in zip(axes, ("D1", "D2")):
        items = []
        for (m, d), pairs in bucket.items():
            if d != ds:
                continue
            ours = sum(a for a, _ in pairs) / len(pairs)
            paper = sum(b for _, b in pairs) / len(pairs)
            items.append((m, ours - paper, ours, paper))
        items.sort(key=lambda x: x[1])
        names = [SHORT[m] for m, *_ in items]
        deltas = [d for _, d, *_ in items]
        colours = [ACCENT if d >= 0 else RED for d in deltas]
        y = np.arange(len(items))
        ax.barh(y, deltas, color=colours, height=0.62)
        ax.set_yticks(y)
        ax.set_yticklabels(names, fontsize=12.5)
        ax.axvline(0, color=INK, lw=1.0)
        for yi, d in zip(y, deltas):
            ax.text(d + (0.004 if d >= 0 else -0.004), yi, f"{d:+.3f}", va="center",
                    ha="left" if d >= 0 else "right", fontsize=11.5, color=INK)
        ax.set_xlim(-0.06, 0.60)
        ax.set_title(f"{ds} — accuracy difference vs. the paper", fontsize=16.5, color=INK,
                     fontweight="bold", pad=10)
        ax.set_xlabel("ours − reported", fontsize=13.5)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    fig.tight_layout()
    _save(fig, "slide_delta.png")


def assets_leakage() -> None:
    path = ROOT / "results" / "leakage.csv"
    if not path.exists():
        return
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    settings = ["full", "small15"]
    models = ["mobilenet_v2", "resnet50", "vgg16"]
    fig, ax = plt.subplots(figsize=(13.2, 5.6))
    width = 0.34
    xs = np.arange(len(settings) * len(models))
    labels = []
    for k, (setting, model) in enumerate((s, m) for s in settings for m in models):
        row = next(r for r in rows if r["setting"] == setting and r["model"] == model)
        rand, group = float(row["accuracy_random"]), float(row["accuracy_group"])
        ax.bar(k - width / 2, rand, width, color=ACCENT_2, label="random split" if k == 0 else None)
        ax.bar(k + width / 2, group, width, color=ACCENT, label="grouped by source" if k == 0 else None)
        ax.text(k - width / 2, rand + 0.0015, f"{rand:.3f}", ha="center", fontsize=11, color=INK)
        ax.text(k + width / 2, group + 0.0015, f"{group:.3f}", ha="center", fontsize=11, color=INK)
        labels.append(f"{SHORT[model]}\n{setting}")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylim(0.94, 1.005)
    ax.set_ylabel("test accuracy")
    ax.legend(frameon=False, loc="lower right")
    ax.axhline(1.0, color=MUTED, lw=1.0, ls=":")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    _save(fig, "slide_leakage.png")


def assets_efficiency() -> None:
    rows = list(csv.DictReader((ROOT / "results" / "efficiency.csv").open(encoding="utf-8")))
    fig, ax = plt.subplots(figsize=(13.2, 5.8))
    for r in rows:
        params = float(r["n_params"])
        cpu = float(r["cpu_ms_per_image"])
        model = r["model"]
        highlight = model in ("mobilenet_v2", "vgg16", "nasnet_large")
        ax.scatter(params, cpu, s=260 if highlight else 150,
                   color=ACCENT if highlight else ACCENT_2,
                   edgecolor=INK if highlight else "none", linewidth=1.2, zorder=3)
    for r in rows:
        model = r["model"]
        if model not in ("mobilenet_v2", "efficientnet_b0", "vgg16", "nasnet_large"):
            continue
        params = float(r["n_params"])
        cpu = float(r["cpu_ms_per_image"])
        dx, dy = 1.12, 1.06
        ax.annotate(SHORT[model], (params, cpu), xytext=(params * dx, cpu * dy),
                    fontsize=13.5, color=INK, fontweight="bold")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("parameters (log scale)")
    ax.set_ylabel("latency on CPU, ms per image (log scale)")
    ax.axhline(33.3, color=AMBER, lw=1.2, ls="--")
    ax.text(2.2e6, 36, "33 ms ≈ 30 FPS", color=AMBER, fontsize=12.5, fontweight="bold")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    _save(fig, "slide_efficiency.png")


def assets_gradcam() -> None:
    """Two samples, three panels each, drawn with large fonts."""
    import torch
    from PIL import Image
    from torchvision import transforms

    from analysis.checkpoint import load_model
    from analysis.gradcam import compute_cam, heat_overlay

    run = ROOT / "results" / "runs" / "mobilenet_v2__D1__adam__s42"
    if not (run / "model.pt").exists():
        print("[assets] gradcam skipped (no checkpoint)")
        return
    net, _ = load_model(run, device="cpu", pretrained=True)
    net.eval()

    tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    samples = [
        (ROOT / "testset" / "D1" / "test" / "defect" / "IMG_9153.jpg", "defect"),
        (ROOT / "testset" / "D1" / "test" / "nondefect" / "IMG_8930.jpg", "no defect"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(12.6, 7.4))
    for row, (path, truth) in zip(axes, samples):
        if not path.exists():
            continue
        im = Image.open(path).convert("RGB")
        # the overlay is computed on a downscaled copy: 5184x3456 float32 would need >1 GB
        scale_w = 620
        im = im.resize((scale_w, int(scale_w * im.height / im.width)), Image.LANCZOS)
        x = tf(im).unsqueeze(0)
        with torch.no_grad():
            probs = torch.softmax(net(x), 1)[0]
        pred = int(probs.argmax())
        cam, _ = compute_cam(net, x, class_idx=pred)
        overlay = heat_overlay(im, cam, alpha=0.5)
        heat = cam / (cam.max() + 1e-8)
        panels = [
            (im, f"input · truth: {truth}", INK),
            (heat, "Grad-CAM (7 × 7, upsampled)", ACCENT),
            (overlay, f"overlay · P(defect) = {probs[1]:.3f}", GREEN if pred == 0 else RED),
        ]
        for ax, (img, title, colour) in zip(row, panels):
            ax.imshow(img, cmap="turbo" if img is heat else None)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.set_title(title, fontsize=15, color=colour, fontweight="bold", pad=8)
    fig.tight_layout()
    _save(fig, "slide_gradcam.png")


def _trim_white(path: Path, pad: int = 10) -> None:
    from PIL import Image, ImageChops

    with Image.open(path) as im:
        rgb = im.convert("RGB")
        bg = Image.new("RGB", rgb.size, (255, 255, 255))
        bbox = ImageChops.difference(rgb, bg).getbbox()
        if not bbox:
            return
        l, t, r, b = bbox
        rgb.crop((max(0, l - pad), max(0, t - pad),
                  min(rgb.width, r + pad), min(rgb.height, b + pad))).save(path)


def assets_network() -> None:
    from tools.make_network_figure import draw

    path = draw(OUT / "slide_network.png", font_scale=1.45, rows=(), compact=True)
    _trim_white(path)
    print(f"[assets] slide_network.png  {path.stat().st_size / 1024:.0f} KB")


TASKS = {
    "samples": assets_samples,
    "augmentation": assets_augmentation,
    "network": assets_network,
    "backbones": assets_backbones,
    "optimizer": assets_optimizer,
    "delta": assets_delta,
    "leakage": assets_leakage,
    "efficiency": assets_efficiency,
    "gradcam": assets_gradcam,
}


def main() -> None:
    ap = argparse.ArgumentParser(description="Render the slide versions of the figures.")
    ap.add_argument("--only", default="", help="comma separated subset, e.g. backbones,delta")
    args = ap.parse_args()
    names = [n.strip() for n in args.only.split(",") if n.strip()] or list(TASKS)
    for name in names:
        fn = TASKS.get(name)
        if fn is None:
            raise SystemExit(f"unknown asset {name}, available: {list(TASKS)}")
        print(f"\n== {name} ==")
        fn()


if __name__ == "__main__":
    main()
