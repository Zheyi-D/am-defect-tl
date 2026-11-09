# Author: Leiman Pan + agent | Task: live demo UI (Gradio) | PR: pending
# Status: built on the Gradio framework (open source, see NOTICE.md); UI logic and inference wrapper written by this group
"""Live demo: upload a photo of a 3D-printed part → defect / nondefect probability + Grad-CAM heatmap.

Usage:
    python -m analysis.demo_app                      # open the browser UI
    python -m analysis.demo_app --warmup             # only pre-load the weights (do this before a talk)
    python -m analysis.demo_app --selftest           # no UI; run one inference pass and exit
    python -m analysis.demo_app --model vgg16 --share
    python -m analysis.demo_app --host 0.0.0.0       # let phones on the same Wi-Fi connect

Two environment variables (for a venue without network):
    HF_HUB_OFFLINE=1        stop timm from downloading backbones from HuggingFace (run --warmup in advance)
    GRADIO_ANALYTICS_ENABLED=False

Only the 5 D1 + Adam runs have a model.pt, so the UI offers only those 5 models; the other 61 runs have
metrics.json only and cannot run inference — this is stated in the UI notes to avoid surprises.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
# Common Windows system proxies (v2rayN etc.) also route 127.0.0.1, which makes Gradio's self-check return 503
for _k in ("NO_PROXY", "no_proxy"):
    _v = os.environ.get(_k, "")
    if "127.0.0.1" not in _v:
        os.environ[_k] = (_v + ",127.0.0.1,localhost").lstrip(",")

ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "results" / "runs"
FIG_DIR = ROOT / "results" / "figures"

PRETTY = {
    "vgg16": "VGG16", "vgg19": "VGG19", "resnet50": "ResNet50", "resnet101": "ResNet101",
    "inception_resnet_v2": "InceptionResNetV2", "xception": "Xception",
    "mobilenet_v2": "MobileNetV2", "efficientnet_b0": "EfficientNet-B0",
    "efficientnet_b7": "EfficientNet-B7", "efficientnet_v2m": "EfficientNetV2-M",
    "nasnet_large": "NASNet-Large",
}

# Model cache: loaded on first use, then kept resident (one forward pass on CPU takes ~0.2–1.5 s)
_CACHE: dict[str, object] = {}


def available_runs() -> list[Path]:
    from analysis.checkpoint import list_checkpoints

    return list_checkpoints(RUNS_DIR)


def label_of(run_dir: Path) -> str:
    """'vgg16__D1__adam__s42' → 'VGG16 · D1 · Adam'"""
    parts = run_dir.name.split("__")
    model = PRETTY.get(parts[0], parts[0])
    ds = parts[1] if len(parts) > 1 else "?"
    opt = (parts[2] if len(parts) > 2 else "?").capitalize()
    tag = f"{model} · {ds} · {opt}"
    if ds == "D2":
        tag = "⚠ " + tag + " (trained on 128px augmented images; comparison only)"
    return tag


def get_model(run_dir: Path):
    key = str(run_dir)
    if key not in _CACHE:
        from analysis.checkpoint import load_model

        model, ckpt = load_model(run_dir, device="cpu", pretrained=True)
        _CACHE[key] = (model, ckpt)
    return _CACHE[key]


def predict_one(run_dir: Path, image_path: str) -> dict:
    """Single-model inference; returns probabilities, the overlay image and the Grad-CAM array.

    Grad-CAM follows the class **the model actually predicted**: when it predicts nondefect it explains the
    nondefect evidence, otherwise the heatmap would show evidence for defect, look almost black on defect-free
    samples and appear broken.
    """
    import numpy as np
    import torch
    from PIL import Image

    from analysis.gradcam import compute_cam, heat_overlay, load_image

    model, ckpt = get_model(run_dir)
    size = int(ckpt.get("input_size", 224))
    x, im = load_image(Path(image_path), size)

    with torch.no_grad():
        probs = torch.softmax(model(x), dim=1)[0].cpu().numpy()
    pred = int(np.argmax(probs))
    cam, _ = compute_cam(model, x, class_idx=pred)

    overlay = heat_overlay(im, cam, alpha=0.5)
    overlay_img = Image.fromarray((np.clip(overlay, 0, 1) * 255).astype("uint8"))
    return {
        "p_defect": float(probs[1]),
        "p_nondefect": float(probs[0]),
        "pred": pred,
        "overlay": overlay_img,
        "cam": cam,
    }


def run_table(image_path: str) -> list[list]:
    """Run the same input through every available checkpoint for a model-to-model comparison."""
    import pandas as pd

    rows = []
    for run_dir in available_runs():
        meta = {}
        try:
            meta = __import__("json").loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
        except Exception:
            pass
        try:
            r = predict_one(run_dir, image_path)
            rows.append([label_of(run_dir), round(r["p_defect"], 3),
                         "defect" if r["p_defect"] >= 0.5 else "nondefect",
                         round(meta.get("metrics", {}).get("test", {}).get("accuracy", float("nan")), 3)])
        except Exception as exc:  # one failing model must not break the whole comparison table
            rows.append([label_of(run_dir), None, f"failed to load: {type(exc).__name__}", None])
    return rows


def ui_predict(image_path, run_label, compare_all):
    """Gradio callback: returns (Label, overlay image, Markdown notes, comparison table)."""
    import gradio as gr

    if not image_path:
        return None, None, "Upload an image first.", None

    runs = available_runs()
    by_label = {label_of(p): p for p in runs}
    if not runs:
        return None, None, "No model.pt under results/runs; cannot run inference.", None

    run_dir = by_label.get(run_label, runs[0])
    try:
        r = predict_one(run_dir, image_path)
    except Exception as exc:
        # Fallback: show the pre-rendered example figure so a live demo never dies
        fig = FIG_DIR / f"predict_{run_dir.name}.png"
        msg = (f"**Model failed to load**: `{type(exc).__name__}: {exc}`\n\n"
               f"Falling back to the pre-rendered example figure (`{fig.name}`). "
               "If this mentions a download failure, the venue has no network and the weights were not "
               "pre-loaded — run `--warmup` before the talk.")
        return None, str(fig) if fig.exists() else None, msg, None

    meta = {}
    try:
        import json

        meta = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    tm = meta.get("metrics", {}).get("test", {})
    n_test = meta.get("n_test", "?")

    verdict = "defect" if r["p_defect"] >= 0.5 else "nondefect"
    verdict_cn = "defect present" if verdict == "defect" else "no defect"
    prob = {"defect": r["p_defect"], "nondefect": r["p_nondefect"]}

    note = (
        f"**Verdict: `{verdict}` ({verdict_cn})** | P(defect) = `{r['p_defect']:.3f}`\n\n"
        f"The heatmap explains **this verdict** ({'defect' if r.get('pred', 1) == 1 else 'nondefect'}); "
        "red = regions supporting the verdict, blue = opposing it.\n\n"
        f"Overall performance of this model on the D1 test set (n={n_test}): "
        f"acc `{tm.get('accuracy', float('nan')):.3f}` · F1 `{tm.get('f1', float('nan')):.3f}` · "
        f"MCC `{tm.get('mcc', float('nan')):.3f}`.\n\n"
        "A single image does not represent overall accuracy — the test set has only 54 images, so one "
        "mistake costs 1.8 percentage points.\n\n"
        "The heatmap is Grad-CAM: red regions are where the model looked most when deciding. If the red lands "
        "on the background or on reflections, the model learned a spurious correlation."
    )
    table = run_table(image_path) if compare_all else None
    return prob, r["overlay"], note, table


def demo_examples(per_class: int = 2) -> list[Path]:
    """UI example images: prefer samples/D1_test (drawn from the D1 test set, never seen in training).

    Falls back to samples/D1 (224px debug images prepared by Kenneth, including many hard edge cases).
    """
    for base in ("D1_test", "D1"):
        out = []
        for label in ("defect", "nondefect"):
            d = ROOT / "samples" / base / label
            if d.exists():
                out += sorted(x for x in d.iterdir()
                              if x.suffix.lower() in {".jpg", ".jpeg", ".png"})[:per_class]
        if len(out) == 2 * per_class:
            return out
    return out


DEMO_EXAMPLES = demo_examples()


def build_ui(choices: list[str], default: str):
    import gradio as gr

    with gr.Blocks(title="3D-printed part defect detection · transfer-learning reproduction") as demo:
        gr.Markdown(
            "# 3D-printed part defect detection · transfer-learning reproduction\n"
            "**IDAT7215 Group Project · Topic 4** — frozen ImageNet backbones with the paper's classification head.\n\n"
            f"> Models available for inference: {len(choices)} (5 on D1 + 5 on D2, all Adam). The other runs "
            "store metrics only, without weights."
            "  \n> **The D2 checkpoints were trained on 128×128 augmented images and are clearly worse on 224px "
            "originals (only 2–6 of 10 defect samples correct), so use D1 for the demo; D2 is for comparison only.**"
            "  \n> The first inference loads the backbone and takes 3–8 s; switching images afterwards is fast."
        )
        with gr.Row():
            with gr.Column(scale=1):
                img = gr.Image(type="filepath", label="Upload a photo of a 3D-printed part", height=320)
                if DEMO_EXAMPLES:
                    gr.Markdown("Example order: images 1–2 are **defect**, images 3–4 are **nondefect**. "
                                "Click the two defect ones first, then the two nondefect ones.")
                    gr.Examples(examples=[[str(p)] for p in DEMO_EXAMPLES],
                                inputs=[img],
                                label="Examples (D1 test set, unseen in training; 2 per class, hand-picked, "
                                      "not a random sample)")
                model_dd = gr.Dropdown(choices, value=default, label="Model")
                compare = gr.Checkbox(value=False, label="Compare all models (about 5–10 s slower)")
                btn = gr.Button("Predict", variant="primary")
            with gr.Column(scale=1):
                out_label = gr.Label(num_top_classes=2, label="Class probability")
                out_img = gr.Image(label="Grad-CAM (red = model attention)", height=320)
        out_note = gr.Markdown()
        out_table = gr.Dataframe(
            headers=["Model", "P(defect)", "Prediction", "D1 test acc"],
            datatype=["str", "number", "str", "number"],
            label="All-model comparison", wrap=True,
        )
        btn.click(ui_predict, [img, model_dd, compare], [out_label, out_img, out_note, out_table])
        img.change(ui_predict, [img, model_dd, compare], [out_label, out_img, out_note, out_table])
        gr.Markdown(
            "---\n"
            "**Notes**: positive class = `defect`. Preprocessing matches training (direct resize to 224×224, "
            "no aspect-ratio crop). The D1 test set has only 54 images, so a single wrong prediction moves the "
            "overall metric a lot; the UI does not promise generalisation performance."
        )
    return demo


def warmup(verbose: bool = True) -> None:
    """Download the backbone of every checkpoint and run one forward pass; run this before a talk."""
    import numpy as np
    import torch

    runs = available_runs()
    if not runs:
        print("[warmup] no model.pt found")
        return
    dummy = torch.zeros(1, 3, 224, 224)
    for i, run_dir in enumerate(runs, 1):
        try:
            model, ckpt = get_model(run_dir)
            with torch.no_grad():
                logits = model(dummy)
            if verbose:
                print(f"[warmup] {i}/{len(runs)} {label_of(run_dir)} ok "
                      f"(logits {logits.shape})", flush=True)
        except Exception as exc:
            print(f"[warmup] {i}/{len(runs)} {label_of(run_dir)} failed: {type(exc).__name__}: {exc}",
                  flush=True)
    print("[warmup] done. Set HF_HUB_OFFLINE=1 before launching the UI at the venue.")


def selftest() -> int:
    """No UI: run one inference on a synthetic image to verify loading / forward / Grad-CAM end to end."""
    import numpy as np
    from PIL import Image

    runs = available_runs()
    if not runs:
        print("[selftest] no model.pt")
        return 1
    # Use the smallest checkpoint (MobileNetV2) to avoid pulling a 1 GB backbone
    run_dir = min(runs, key=lambda p: (p / "model.pt").stat().st_size)
    tmp = Path(os.environ.get("TEMP", "/tmp")) / "am_defect_selftest.png"
    arr = (np.random.default_rng(0).random((480, 480, 3)) * 255).astype("uint8")
    Image.fromarray(arr).save(tmp)
    r = predict_one(run_dir, str(tmp))
    print(f"[selftest] {label_of(run_dir)} p_defect={r['p_defect']:.4f} "
          f"cam={r['cam'].shape} overlay={r['overlay'].size}")
    print("[selftest] single-model path OK. Run --warmup to verify the remaining models.")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=None, help="vgg16 / resnet50 / ... (defaults to the first available)")
    ap.add_argument("--ckpt", default=None, help="run directory to use directly")
    ap.add_argument("--warmup", action="store_true", help="only pre-load weights, do not launch the UI")
    ap.add_argument("--selftest", action="store_true", help="run one offline inference self-test")
    ap.add_argument("--offline", action="store_true", help="set HF_HUB_OFFLINE=1 (weights must be pre-loaded)")
    ap.add_argument("--mirror", action="store_true",
                    help="download timm weights via hf-mirror.com (when huggingface.co is unreachable in China)")
    ap.add_argument("--share", action="store_true", help="create a public Gradio link (needs network)")
    ap.add_argument("--host", default="127.0.0.1", help="0.0.0.0 = reachable from phones on the same network")
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    if args.offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
    if args.mirror:
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

    if args.warmup:
        warmup()
        return
    if args.selftest:
        raise SystemExit(selftest())

    runs = available_runs()
    if not runs:
        raise SystemExit("No model.pt under results/runs; cannot start the demo.")
    if args.ckpt:
        run_dir = Path(args.ckpt)
        if not run_dir.is_absolute():
            run_dir = RUNS_DIR / args.ckpt
        runs = [run_dir] + [r for r in runs if r != run_dir]
    elif args.model:
        picked = [r for r in runs if r.name.split("__")[0] == args.model]
        if picked:
            runs = picked + [r for r in runs if r not in picked]

    # Default to MobileNetV2: fastest to load on CPU, so live switching stays responsive
    order = ["mobilenet_v2", "vgg16", "resnet50", "xception", "inception_resnet_v2"]
    runs = sorted(runs, key=lambda p: (order.index(p.name.split("__")[0])
                                       if p.name.split("__")[0] in order else 99))
    choices = [label_of(r) for r in runs]
    import gradio as gr

    kwargs = dict(server_name=args.host, server_port=args.port, share=args.share,
                  inbrowser=not args.no_browser, show_error=True)
    try:  # Gradio 6 moved theme from Blocks to launch; older versions still accept it on Blocks
        build_ui(choices, choices[0]).launch(theme=gr.themes.Soft(), **kwargs)
    except TypeError:
        build_ui(choices, choices[0]).launch(**kwargs)


if __name__ == "__main__":
    main()
