# Author: Lead + agent | Task: model factory (11 backbones + freezing + paper-style head) | PR: TBD
# Status: original implementation by this team. Uses timm ImageNet pretrained weights (unmodified, see NOTICE.md)
"""11 backbones plus frozen convolution layers plus the paper's classification head.

Paper setup (arXiv:2310.08645 section 4.3, cross-checked against the authors' notebook):
    backbone output -> AveragePooling2D((4,4)) -> Flatten -> Dense(64, relu) -> Dropout(0.5) -> Dense(2)
    All convolution layers are frozen during training and only the new head is trained.

Everything is loaded through timm (torchvision lacks NASNet / Xception / InceptionResNetV2 / EfficientNetV2M).
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

# config model name -> timm model name (the list holds candidate names, tried in order; the first one that
# loads pretrained weights wins)
# Note: some legacy names in timm no longer ship default pretrained weights (e.g. efficientnet_b7),
#       hence the fallback candidates so that one model cannot block the whole experiment batch.
BACKBONES = {
    "vgg16": ["vgg16"],
    "vgg19": ["vgg19"],
    "resnet50": ["resnet50"],
    "resnet101": ["resnet101"],
    "inception_resnet_v2": ["inception_resnet_v2"],
    "xception": ["xception"],
    "mobilenet_v2": ["mobilenetv2_100"],
    "efficientnet_b0": ["efficientnet_b0", "tf_efficientnet_b0"],
    "efficientnet_b7": ["tf_efficientnet_b7", "efficientnet_b7.ra_in1k", "efficientnet_b7"],
    "efficientnet_v2m": ["tf_efficientnetv2_m", "efficientnetv2_m"],
    "nasnet_large": ["nasnetalarge"],
}


class PaperHead(nn.Module):
    """The paper's classification head: AvgPool(4,4) -> Flatten -> Dense(64,relu) -> Dropout -> Dense(2)."""

    def __init__(self, in_ch: int, num_classes: int = 2, dense_units: int = 64,
                 dropout: float = 0.5, pool: int = 4, spatial: int = 7):
        super().__init__()
        # The paper uses pool_size=(4,4); if the feature map is smaller than 4x4 fall back to global
        # average pooling (this is reported in the logs)
        self.pool = nn.AvgPool2d(pool) if spatial >= pool else nn.AdaptiveAvgPool2d(1)
        self.fc1 = nn.Linear(in_ch, dense_units)
        self.drop = nn.Dropout(dropout)
        self.fc2 = nn.Linear(dense_units, num_classes)

    def forward(self, x):
        x = torch.flatten(self.pool(x), 1)
        x = F.relu(self.fc1(x))
        x = self.drop(x)
        return self.fc2(x)


class TransferModel(nn.Module):
    """Frozen backbone plus a trainable classification head. The backbone runs under no_grad in forward,
    which saves memory and is faster."""

    def __init__(self, name: str, num_classes: int = 2, pretrained: bool = True,
                 freeze: str = "all_conv", dense_units: int = 64,
                 dropout: float = 0.5, input_size: int = 224):
        super().__init__()
        import timm

        if name not in BACKBONES:
            raise KeyError(f"unknown model {name}, available: {list(BACKBONES)}")
        self.name = name
        self.freeze = freeze

        # Try the candidate names in order: some legacy timm names have no default pretrained weights
        last_err = None
        self.net = None
        for candidate in BACKBONES[name]:
            try:
                self.net = timm.create_model(candidate, pretrained=pretrained, num_classes=0)
                self.timm_name = candidate
                break
            except Exception as exc:
                last_err = exc
                print(f"[models] {name} candidate {candidate} failed to load: {type(exc).__name__}: {exc}", flush=True)
        if self.net is None:
            raise RuntimeError(f"all candidate names failed for {name}, last error: {last_err}")

        if freeze == "all_conv":
            for p in self.net.parameters():
                p.requires_grad = False

        # Probe: run one all-zero image to get the channel count and feature-map size, avoiding a hardcoded
        # shape for every model
        self.net.eval()
        with torch.no_grad():
            feat = self.net.forward_features(torch.zeros(1, 3, input_size, input_size))
        if feat.dim() != 4:
            raise RuntimeError(f"forward_features of {name} returned {tuple(feat.shape)}, expected a 4-D feature map")
        self.feat_shape = tuple(int(v) for v in feat.shape[1:])  # (C, H, W)
        in_ch, h, w = self.feat_shape
        self.head = PaperHead(in_ch, num_classes, dense_units, dropout,
                              pool=4, spatial=min(h, w))

    def train(self, mode: bool = True):
        super().train(mode)
        if self.freeze == "all_conv":
            self.net.eval()  # keep the BN statistics unchanged while the backbone is frozen
        return self

    def forward(self, x):
        if self.freeze == "all_conv":
            with torch.no_grad():
                feat = self.net.forward_features(x)
        else:
            feat = self.net.forward_features(x)
        return self.head(feat)


def count_params(model: nn.Module) -> tuple[int, int]:
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable
