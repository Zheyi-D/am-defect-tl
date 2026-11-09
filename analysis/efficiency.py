# Author: jellyfishhamburger | Task: T3 efficiency measurement (CPU) | PR: pending
# Status: original implementation
"""Efficiency measurement: parameter count / FLOPs / single-image latency → results/efficiency.csv + fig_efficiency.png (T3).

Why this matters: the project is about "online quality inspection for 3D printing", so accuracy alone is not
enough — we also need to show that lightweight models are deployable.

Usage:
    python -m analysis.efficiency                 # all 11 backbones on CPU
    python -m analysis.efficiency --models vgg16,mobilenet_v2
    python -m analysis.efficiency --iters 30

Notes:
    - Building a backbone for the first time downloads ImageNet weights from timm (100–600 MB per model),
      cached afterwards. This task measures **inference** cost only; whether the weights are pretrained
      barely affects latency, but pretrained=True keeps the model identical to training.
    - GPU latency cannot be measured on this machine (no GPU); the CSV stores N/A for Kenneth to fill in
      on Kaggle.
    - **Measure on an idle machine**: parallel weight downloads / LIME runs inflate the mean by 40–100%
      (measured: EfficientNetV2-M went from 161.8 to 344.9 ms). Make sure no other python process is
      running before re-measuring.
    - Writes nothing under src/ and never modifies metrics.json.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGDIR = RESULTS / "figures"
DISPLAY = {
    "vgg16": "VGG16", "vgg19": "VGG19", "resnet50": "ResNet50", "resnet101": "ResNet101",
    "inception_resnet_v2": "InceptionResNetV2", "xception": "Xception",
    "mobilenet_v2": "MobileNetV2", "efficientnet_b0": "EfficientNet-B0",
    "efficientnet_b7": "EfficientNet-B7", "efficientnet_v2m": "EfficientNetV2-M",
    "nasnet_large": "NASNet-Large",
}
ORDER = ["mobilenet_v2", "efficientnet_b0", "resnet50", "xception", "inception_resnet_v2",
         "efficientnet_v2m", "efficientnet_b7", "resnet101", "vgg16", "vgg19", "nasnet_large"]

COLUMNS = ["model", "n_params", "n_params_trainable", "gflops",
           "cpu_ms_per_image", "gpu_ms_per_image"]


def measure_params(model) -> tuple[int, int]:
    """(total parameters, trainable parameters). With a frozen backbone only the head is trainable."""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return int(total), int(trainable)


def measure_flops(model, input_size: int = 224) -> float:
    """GFLOPs (forward, batch=1). Prefer torch's built-in FLOP counter to avoid extra dependencies."""
    import torch

    x = torch.zeros(1, 3, input_size, input_size)
    try:
        from torch.utils.flop_counter import FlopCounterMode

        counter = FlopCounterMode(display=False)
        with counter, torch.no_grad():
            model(x)
        total = counter.get_total_flops()
        return total / 1e9
    except Exception:
        return float("nan")


def measure_latency(model, input_size: int = 224, device: str = "cpu",
                    warmup: int = 5, iters: int = 20) -> dict:
    """Return {mean_ms, p95_ms}: time iters runs after warmup passes."""
    import torch

    model.eval()
    x = torch.zeros(1, 3, input_size, input_size, device=device)
    with torch.no_grad():
        for _ in range(warmup):
            model(x)
        samples = []
        for _ in range(iters):
            t0 = time.perf_counter()
            model(x)
            samples.append((time.perf_counter() - t0) * 1000.0)
    samples.sort()
    return {
        "mean_ms": statistics.fmean(samples),
        "median_ms": statistics.median(samples),
        "p95_ms": samples[min(len(samples) - 1, int(round(0.95 * (len(samples) - 1))))],
    }


def draw_figure(rows: list[dict], out: Path) -> None:
    """fig_efficiency.png: CPU single-image latency (horizontal bars) annotated with parameter counts."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
        "axes.spines.right": False, "grid.color": "#E5E0D5", "legend.frameon": False,
        "savefig.dpi": 200, "savefig.bbox": "tight",
    })
    rows = sorted([r for r in rows if r.get("cpu_ms_per_image")], key=lambda r: r["cpu_ms_per_image"])
    names = [DISPLAY.get(r["model"], r["model"]) for r in rows]
    vals = [r["cpu_ms_per_image"] for r in rows]
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    bars = ax.barh(range(len(rows)), vals, color="#16233A", height=0.62, zorder=2)
    for b, r in zip(bars, rows):
        label = f"{r['cpu_ms_per_image']:.0f} ms · {r['n_params']/1e6:.1f} M params"
        if r.get("gflops") == r.get("gflops"):  # not NaN
            label += f" · {r['gflops']:.1f} GFLOPs"
        ax.annotate(label, xy=(b.get_width(), b.get_y() + b.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    va="center", ha="left", fontsize=6.8, color="#374151")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(names)
    ax.set_xlabel("CPU inference time per image (ms, batch 1, 224×224)")
    ax.set_xlim(0, max(vals) * 1.55)
    ax.grid(axis="x", zorder=0)
    ax.set_axisbelow(True)
    ax.set_title("Inference cost of the 11 backbones (frozen, head only)")
    fig.text(0.01, -0.03,
             "Measured on the author's laptop CPU (no GPU). Absolute numbers are machine-specific; "
             "the relative ordering is what matters.",
             fontsize=6.6, color="#6B7280")
    fig.savefig(out / "fig_efficiency.png")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="all", help="comma-separated; all = 11 backbones")
    ap.add_argument("--iters", type=int, default=20, help="number of timed repetitions (default 20)")
    ap.add_argument("--warmup", type=int, default=5)
    ap.add_argument("--out", type=Path, default=RESULTS / "efficiency.csv")
    ap.add_argument("--replot", action="store_true",
                    help="do not re-measure; replot from the existing efficiency.csv")
    args = ap.parse_args()

    if args.replot:
        if not args.out.exists():
            raise SystemExit(f"{args.out} does not exist; run a full measurement first")
        with args.out.open(encoding="utf-8-sig", newline="") as fh:
            rows = []
            for r in csv.DictReader(fh):
                for k in ("n_params", "n_params_trainable", "gflops", "cpu_ms_per_image"):
                    r[k] = float(r[k]) if r.get(k) not in ("", None) else float("nan")
                rows.append(r)
        FIGDIR.mkdir(parents=True, exist_ok=True)
        draw_figure(rows, FIGDIR)
        print(f"[efficiency] replotted → {FIGDIR / 'fig_efficiency.png'}")
        return

    import torch

    from src.models import TransferModel

    wanted = None if args.models == "all" else {m.strip() for m in args.models.split(",")}
    models = [m for m in ORDER if wanted is None or m in wanted]
    if not models:
        raise SystemExit(f"no matching models: {args.models}")

    rows = []
    for i, name in enumerate(models, 1):
        t0 = time.time()
        try:
            model = TransferModel(name, pretrained=True, freeze="all_conv", input_size=224)
            model.eval()
        except Exception as exc:
            print(f"[efficiency] {i}/{len(models)} {name} failed to build: {type(exc).__name__}: {exc}", flush=True)
            continue
        total, trainable = measure_params(model)
        gflops = measure_flops(model)
        lat = measure_latency(model, iters=args.iters, warmup=args.warmup)
        rows.append({
            "model": name,
            "n_params": total,
            "n_params_trainable": trainable,
            "gflops": round(gflops, 3) if gflops == gflops else float("nan"),
            "cpu_ms_per_image": round(lat["mean_ms"], 1),
            "gpu_ms_per_image": "N/A",
        })
        print(f"[efficiency] {i}/{len(models)} {DISPLAY.get(name, name)}: "
              f"{total/1e6:.1f}M params, {gflops:.2f} GFLOPs, "
              f"{lat['mean_ms']:.1f} ms (median {lat['median_ms']:.1f}) — {time.time()-t0:.0f}s",
              flush=True)

    if not rows:
        raise SystemExit("no model was measured successfully")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if isinstance(r.get(k), float) and r.get(k) != r.get(k) else r.get(k, ""))
                        for k in COLUMNS})
    print(f"[efficiency] {len(rows)} rows → {args.out}")

    FIGDIR.mkdir(parents=True, exist_ok=True)
    draw_figure([r for r in rows], FIGDIR)
    print(f"[efficiency] figure → {FIGDIR / 'fig_efficiency.png'}")


if __name__ == "__main__":
    main()
