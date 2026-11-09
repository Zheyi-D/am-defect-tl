# Author: Kenneth | Task: T3 的 GPU 时延补测 | PR: 待提
# Status: 本组原创实现
"""在 GPU 上测 11 个骨干的单张推理时延，补全 results/efficiency.csv 的 gpu_ms_per_image 列。

为什么单独写脚本：
    `analysis/efficiency.py`（jellyfishhamburger 写的）负责参数量 / FLOPs / CPU 时延，
    其 GPU 列在本地无 GPU 的环境下写 N/A。本脚本只做 GPU 那一段，产物单独一个 csv，
    再由本地合并进 efficiency.csv —— 这样两边的测量互不覆盖，来源清晰。

测法：
    每个骨干 warmup 后重复 iters 次单张前向（batch=1, 224×224），用 CUDA event 计时，
    取中位数（比均值抗抖动）。

用法：
    python tools/measure_gpu_latency.py --iters 50 --out /kaggle/working/results/efficiency_gpu.csv
"""

from __future__ import annotations

import argparse
import csv
import gc
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODELS = [
    "vgg16", "vgg19", "resnet50", "resnet101", "inception_resnet_v2",
    "xception", "mobilenet_v2", "efficientnet_b0", "efficientnet_b7",
    "efficientnet_v2m", "nasnet_large",
]


def measure(model, iters: int, warmup: int, input_size: int) -> dict:
    import torch

    device = torch.device("cuda")
    x = torch.zeros(1, 3, input_size, input_size, device=device)
    model = model.to(device).eval()

    with torch.no_grad():
        for _ in range(warmup):
            model(x)
        torch.cuda.synchronize()

        times = []
        for _ in range(iters):
            start = torch.cuda.Event(enable_timing=True)
            end = torch.cuda.Event(enable_timing=True)
            start.record()
            model(x)
            end.record()
            torch.cuda.synchronize()
            times.append(start.elapsed_time(end))

    times.sort()
    return {
        "mean_ms": round(statistics.mean(times), 2),
        "median_ms": round(statistics.median(times), 2),
        "p95_ms": round(times[int(0.95 * (len(times) - 1))], 2),
        "min_ms": round(times[0], 2),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="all")
    ap.add_argument("--iters", type=int, default=50)
    ap.add_argument("--warmup", type=int, default=5)
    ap.add_argument("--input-size", type=int, default=224)
    ap.add_argument("--out", type=Path, default=Path("results/efficiency_gpu.csv"))
    args = ap.parse_args()

    import torch
    from src.models import TransferModel

    if not torch.cuda.is_available():
        raise SystemExit("没有可用 GPU；本脚本只能在 CUDA 环境运行")

    gpu_name = torch.cuda.get_device_name(0)
    models = MODELS if args.models == "all" else [m.strip() for m in args.models.split(",")]
    print(f"[gpu] device={gpu_name}  iters={args.iters}  warmup={args.warmup}", flush=True)

    rows = []
    for name in models:
        print(f"[gpu] {name} ...", flush=True)
        model = TransferModel(name, num_classes=2, pretrained=True,
                              freeze="all_conv", input_size=args.input_size)
        stats = measure(model, args.iters, args.warmup, args.input_size)
        rows.append({"model": name, **stats, "gpu_name": gpu_name})
        print(f"[gpu]   median={stats['median_ms']} ms  mean={stats['mean_ms']} ms  "
              f"p95={stats['p95_ms']} ms", flush=True)
        del model
        gc.collect()
        torch.cuda.empty_cache()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["model", "mean_ms", "median_ms", "p95_ms", "min_ms", "gpu_name"]
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"[gpu] 写出 {out}（{len(rows)} 行）", flush=True)


if __name__ == "__main__":
    main()
