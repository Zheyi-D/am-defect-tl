# Author: Leiman Pan + agent | Task: checkpoint restoration (shared by inference / Grad-CAM) | PR: pending
# Status: original implementation. Solves the mismatch between archived heads and the current src/models.py definition.
"""Restore a runnable model from results/runs/<run_id>/model.pt.

Why a separate module:
    The 5 model.pt files in the repo store only the classification head (the backbone is ImageNet-pretrained
    and can be rebuilt from timm at any time). But the archives were saved with a "global average pooling"
    head (fc1 input dimension = number of channels C), whereas PaperHead in src/models.py uses
    AvgPool2d(4) when the feature map is at least 4×4 (fc1 input dimension = C×16).
    Loading a checkpoint straight into PaperHead raises:
        RuntimeError: size mismatch for head.fc1.weight: copying a param with shape
        torch.Size([64, 512]) ... current model has torch.Size([64, 8192])
    So we pick the pooling mode from the real fc1.weight shape in the checkpoint; both archive formats
    load correctly, and src/models.py (a shared file owned by the foundation team) stays untouched.

Usage:
    from analysis.checkpoint import load_model, list_checkpoints
    model, ckpt = load_model("results/runs/vgg16__D1__adam__s42", device="cpu")
"""

from __future__ import annotations

from pathlib import Path

import torch
import torch.nn as nn

from src.models import TransferModel


class GlobalPoolHead(nn.Module):
    """Head matching the archives: global average pooling → Flatten → Linear → ReLU → Dropout → Linear."""

    def __init__(self, in_ch: int, num_classes: int = 2, dense_units: int = 64,
                 dropout: float = 0.5):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc1 = nn.Linear(in_ch, dense_units)
        self.drop = nn.Dropout(dropout)
        self.fc2 = nn.Linear(dense_units, num_classes)

    def forward(self, feat: torch.Tensor) -> torch.Tensor:
        x = torch.flatten(self.pool(feat), 1)
        x = torch.relu(self.fc1(x))
        return self.fc2(self.drop(x))


def load_model(run_dir: str | Path, device: str | torch.device = "cpu",
               pretrained: bool = True) -> tuple[TransferModel, dict]:
    """Restore a model. Returns (model, raw checkpoint dict).

    pretrained=True pulls ImageNet weights from timm (needs network the first time, cached afterwards);
    before a demo run `python -m analysis.demo_app --warmup` once to download the weights.
    """
    run_dir = Path(run_dir)
    ckpt_path = run_dir / "model.pt"
    if not ckpt_path.exists():
        raise FileNotFoundError(f"{ckpt_path} does not exist (runs without weights in Git cannot be restored)")

    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model = TransferModel(
        ckpt["model"],
        num_classes=int(ckpt.get("num_classes", 2)),
        pretrained=pretrained,
        freeze=ckpt.get("freeze", "all_conv"),
        dense_units=int(ckpt.get("dense_units", 64)),
        dropout=float(ckpt.get("dropout", 0.5)),
        input_size=int(ckpt.get("input_size", 224)),
    )

    state = ckpt["head_state"]
    fc1_w = state["fc1.weight"]
    in_ch = int(ckpt.get("feat_shape", [fc1_w.shape[1]])[0])
    if int(fc1_w.shape[1]) == in_ch:
        head = GlobalPoolHead(in_ch, int(ckpt.get("num_classes", 2)),
                              int(ckpt.get("dense_units", 64)),
                              float(ckpt.get("dropout", 0.5)))
    elif int(fc1_w.shape[1]) == model.head.fc1.in_features:
        head = model.head
    else:
        raise RuntimeError(
            f"head shape mismatch: archived fc1={tuple(fc1_w.shape)}, "
            f"feature channels C={in_ch}, current PaperHead expects {model.head.fc1.in_features}. "
            "Check whether the checkpoint comes from a different model.")

    head.load_state_dict(state)
    model.head = head
    model.to(device).eval()
    return model, ckpt


def list_checkpoints(runs_dir: str | Path = "results/runs") -> list[Path]:
    """All run directories containing model.pt, sorted by dataset/model name."""
    runs_dir = Path(runs_dir)
    if not runs_dir.exists():
        return []
    return sorted(p for p in runs_dir.iterdir() if (p / "model.pt").exists())


def run_meta(run_dir: str | Path) -> dict:
    """Read display metadata from metrics.json in the same directory (empty dict if absent)."""
    import json

    p = Path(run_dir) / "metrics.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))
