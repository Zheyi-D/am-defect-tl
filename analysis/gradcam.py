# Author: team lead + agent | Task: Grad-CAM explainability + prediction example figures | PR: pending
# Status: original implementation (CAM algorithm implemented here; matplotlib only handles colour mapping)
"""Generate two kinds of figures (report figures + demo assets):
    1. results/figures/gradcam_<run_id>.png  — original image + Grad-CAM heatmap overlay, with true/pred/confidence
    2. results/figures/predict_<run_id>.png  — original image + predicted label + confidence + correct/wrong mark

Prerequisite: the corresponding run directory must contain model.pt (produced by `src.train --save-weights`,
head only).

How it works (Grad-CAM):
    Let gradients flow to the last feature map F (C×H×W) of the backbone output,
    differentiate the target-class logit, giving weights w_c = mean(∂y/∂F_c),
    CAM = ReLU(Σ_c w_c · F_c), normalised to 0–1 and upsampled onto the original image.

Usage:
    python -m analysis.gradcam --data-root <data root> --cache-root /kaggle/temp/cache \
        --models vgg16,mobilenet_v2 --dataset D1 --n-per-class 4
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from src.dataset import IMAGENET_MEAN, IMAGENET_STD, read_split
from src.models import TransferModel


def load_trained(run_dir: Path, device):
    """Restore a model from model.pt (delegates to analysis.checkpoint: handles global-pooling heads)."""
    from analysis.checkpoint import load_model

    return load_model(run_dir, device=device)


def resolve_path(cache_root, data_root, rel_path: str) -> Path:
    rel = str(rel_path).replace("\\", "/")
    if cache_root:
        parts = rel.split("/")
        if len(parts) >= 4 and parts[0] == "data":
            fname = Path("/".join(parts[3:])).stem + ".jpg"
            return Path(cache_root) / parts[1] / parts[2] / fname
    return Path(data_root) / rel


def load_image(path: Path, size: int):
    im = Image.open(path).convert("RGB").resize((size, size), Image.BILINEAR)
    arr = np.asarray(im, dtype=np.float32) / 255.0
    t = torch.from_numpy(arr).permute(2, 0, 1)
    t = (t - torch.tensor(IMAGENET_MEAN)[:, None, None]) / torch.tensor(IMAGENET_STD)[:, None, None]
    return t.unsqueeze(0), im


def compute_cam(model, x: torch.Tensor, class_idx: int = 1):
    """Return (H×W numpy CAM scaled to 0–1, softmax probabilities numpy)."""
    x = x.clone().requires_grad_(True)  # let gradients reach the feature map
    feat = model.net.forward_features(x)
    feat.retain_grad()
    logits = model.head(feat)
    model.zero_grad(set_to_none=True)
    logits[0, class_idx].backward()

    grads = feat.grad[0]
    feats = feat[0]
    weights = grads.mean(dim=(1, 2))                     # importance of each channel
    cam = torch.relu((weights[:, None, None] * feats).sum(0))
    cam = cam.detach().cpu().numpy()
    cam -= cam.min()
    cam /= (cam.max() + 1e-8)
    probs = torch.softmax(logits.detach(), dim=1)[0].cpu().numpy()
    return cam, probs


def heat_overlay(im: Image.Image, cam: np.ndarray, alpha: float = 0.45):
    import matplotlib.cm as cm

    cam_img = Image.fromarray((cam * 255).astype(np.uint8)).resize(im.size, Image.BILINEAR)
    heat = cm.jet(np.asarray(cam_img, dtype=np.float32) / 255.0)[..., :3]
    base = np.asarray(im, dtype=np.float32) / 255.0
    return np.clip((1 - alpha) * base + alpha * heat, 0, 1)


def pick_samples(rows: list[dict], n_per_class: int) -> list[dict]:
    out = []
    for label in ("defect", "nondefect"):
        out.extend([r for r in rows if r["label"] == label][:n_per_class])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path, required=True)
    ap.add_argument("--cache-root", type=Path, default=None)
    ap.add_argument("--splits-dir", type=Path, default=Path("splits"))
    ap.add_argument("--runs-dir", type=Path, default=Path("results/runs"))
    ap.add_argument("--out", type=Path, default=Path("results/figures"))
    ap.add_argument("--models", default="all")
    ap.add_argument("--dataset", default="D1")
    ap.add_argument("--n-per-class", type=int, default=4)
    args = ap.parse_args()

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    args.out.mkdir(parents=True, exist_ok=True)
    rows = read_split(Path(args.splits_dir) / f"{args.dataset}.csv", "test")
    samples = pick_samples(rows, args.n_per_class)
    if not samples:
        raise RuntimeError("test split is empty; check the splits directory")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    wanted = None if args.models == "all" else {m.strip() for m in args.models.split(",")}
    run_dirs = []
    for p in sorted(Path(args.runs_dir).glob(f"*__{args.dataset}__*")):
        if not (p / "model.pt").exists():
            continue
        if wanted is None or p.name.split("__")[0] in wanted:
            run_dirs.append(p)
    print(f"[gradcam] found {len(run_dirs)} runs with model.pt", flush=True)

    for run_dir in run_dirs:
        model, ckpt = load_trained(run_dir, device)
        size = int(ckpt.get("input_size", 224))
        ims, cams, probs, trues = [], [], [], []
        for r in samples:
            img_path = resolve_path(args.cache_root, args.data_root, r["path"])
            x, im = load_image(img_path, size)
            cam, p = compute_cam(model, x.to(device), class_idx=1)
            ims.append(im)
            cams.append(cam)
            probs.append(p)
            trues.append(r["label"])

        n = len(samples)
        # (1) Grad-CAM figure
        fig, axes = plt.subplots(1, n, figsize=(2.4 * n, 3.0))
        axes = np.atleast_1d(axes)
        for ax, im, cam, p, t in zip(axes, ims, cams, probs, trues):
            ax.imshow(im)
            ax.imshow(heat_overlay(im, cam), alpha=0.55)
            ax.axis("off")
            pred = "defect" if p[1] >= 0.5 else "nondefect"
            ax.set_title(f"true={t}\npred={pred} (p={p[1]:.2f})", fontsize=8)
        fig.suptitle(f"{run_dir.name} — Grad-CAM (red = model attention)", fontsize=10)
        fig.tight_layout()
        fig.savefig(args.out / f"gradcam_{run_dir.name}.png", dpi=140)
        plt.close(fig)

        # (2) Prediction example figure
        fig, axes = plt.subplots(1, n, figsize=(2.4 * n, 2.7))
        axes = np.atleast_1d(axes)
        for ax, im, p, t in zip(axes, ims, probs, trues):
            ax.imshow(im)
            ax.axis("off")
            pred = "defect" if p[1] >= 0.5 else "nondefect"
            mark = "OK" if pred == t else "WRONG"
            ax.set_title(f"true={t}\npred={pred} ({p[1]:.2f}) {mark}", fontsize=8)
        fig.suptitle(f"{run_dir.name} — predictions", fontsize=10)
        fig.tight_layout()
        fig.savefig(args.out / f"predict_{run_dir.name}.png", dpi=140)
        plt.close(fig)
        print(f"[gradcam] {run_dir.name} -> gradcam + predict", flush=True)


if __name__ == "__main__":
    main()
