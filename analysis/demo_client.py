# Author: Kenneth + agent | Task: client-facing inspection UI (Gradio) | Status: new file, technical version untouched
"""Client-facing inspection station: upload a part photo -> scan animation -> PASS / FAIL verdict.

This is the *customer* build. It deliberately hides all research detail
(backbones, datasets, optimisers, metrics, Grad-CAM naming) and exposes only
what an operator needs: a verdict, a confidence, the defect location and a log.

Engine (fixed, D1 weights only):
    mobilenet_v2__D1__adam__s42   -- 1.0000 test accuracy on D1 (ties with the
    other four D1 checkpoints) at 2.3 M parameters / 22.9 ms per image on CPU,
    i.e. the cheapest model that loses nothing on accuracy.

The five D2 checkpoints are never exposed: they were trained on 128x128
augmented images and collapse on 224 px originals.

Usage:
    python -m analysis.demo_client                     # http://127.0.0.1:7861
    python -m analysis.demo_client --selftest          # one inference, print, exit
    python -m analysis.demo_client --host 0.0.0.0      # reachable from a phone
    python -m analysis.demo_client --model resnet50    # hidden switch for Q&A
"""

from __future__ import annotations

import argparse
import base64
import csv
import io
import os
import time
from datetime import datetime
from pathlib import Path

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
for _k in ("NO_PROXY", "no_proxy"):
    _v = os.environ.get(_k, "")
    if "127.0.0.1" not in _v:
        os.environ[_k] = (_v + ",127.0.0.1,localhost").lstrip(",")

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "results" / "runs"

DEFAULT_MODEL = "mobilenet_v2"
DATASET = "D1"
OPTIMIZER = "adam"
SEED = 42

THRESHOLD = 0.50          # decision boundary
REVIEW_BAND = (0.35, 0.65)  # inside this band the verdict is "needs review"
SCAN_SECONDS = 1.15       # must match the CSS animation duration

_ENGINE: dict[str, object] = {}


# ---------------------------------------------------------------- engine
def run_dir_for(model: str) -> Path:
    run = RUNS / f"{model}__{DATASET}__{OPTIMIZER}__s{SEED}"
    if not (run / "model.pt").exists():
        raise SystemExit(f"no checkpoint for {model} at {run}")
    return run


def engine(model: str):
    """Load (once) the frozen backbone + the trained head."""
    if model not in _ENGINE:
        from analysis.checkpoint import load_model

        run = run_dir_for(model)
        net, ckpt = load_model(run, device="cpu", pretrained=True)
        net.eval()
        _ENGINE[model] = net
    return _ENGINE[model]


def predict(pil_image, model: str) -> dict:
    """One inference: probability, verdict, Grad-CAM overlay, cycle time."""
    import torch
    from PIL import Image
    from torchvision import transforms

    from analysis.gradcam import compute_cam, heat_overlay

    t0 = time.perf_counter()
    net = engine(model)

    tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    im = pil_image.convert("RGB")
    x = tf(im).unsqueeze(0)

    with torch.no_grad():
        probs = torch.softmax(net(x), dim=1)[0].cpu().numpy()
    p_defect = float(probs[1])

    lo, hi = REVIEW_BAND
    if p_defect >= hi:
        verdict, cls = "FAIL", "bad"
        desc = "Surface irregularity detected. Reject or send for rework."
    elif p_defect <= lo:
        verdict, cls = "PASS", "ok"
        desc = "No surface defect detected."
    else:
        verdict, cls = "REVIEW", "warn"
        desc = "Verdict unclear. Re-shoot under better lighting or inspect manually."

    # Grad-CAM explains the class the model actually leaned towards
    pred_idx = 1 if p_defect >= 0.5 else 0
    cam, _ = compute_cam(net, x, class_idx=pred_idx)
    overlay = heat_overlay(im, cam, alpha=0.5)

    cycle = time.perf_counter() - t0
    return {
        "verdict": verdict,
        "cls": cls,
        "desc": desc,
        "p_defect": p_defect,
        "confidence": max(p_defect, 1.0 - p_defect),
        "overlay": overlay,
        "cycle": cycle,
        "model": model,
    }


# ---------------------------------------------------------------- html bits
def _b64(image, size: int = 720) -> str:
    from PIL import Image

    im = image.convert("RGB")
    im.thumbnail((size, size), Image.BILINEAR)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode("ascii")


HUD = """
<div class="hud-tag tl">TARGET · LOCKED</div>
<div class="hud-tag tr">{state}</div>
<div class="hud-tag bl">FOCUS 0.94</div>
<div class="hud-tag br2">{time}</div>
<div class="br tl"></div><div class="br tr"></div><div class="br bl"></div><div class="br br2"></div>
"""


def viewport_html(img_b64: str | None, state: str, time_text: str,
                  scanning: bool = False, progress: int = 0) -> str:
    if img_b64 is None:
        inner = (
            '<div class="awaiting"><div class="aw-ico">⤒</div>'
            '<div class="aw-1">NO PART LOADED</div>'
            '<div class="aw-2">Load a photo, then press <b>Scan part</b></div></div>'
        )
        return f'<div class="bezel-in"><div class="screen idle">{inner}</div></div>'

    cls = "screen"
    if scanning:
        cls += " scanning"
    extra = ""
    if scanning:
        p_pct = max(0, min(100, progress))
        extra = f'<div class="prog"><i style="width:{p_pct}%"></i></div>'
        extra += f'<div class="prog-text">SCAN {p_pct}%</div>' 
    laser = '<div class="laser"></div><div class="trail"></div><div class="scanline"></div>'
    return (
        f'<div class="bezel-in"><div class="{cls}">'
        f'<img src="data:image/jpeg;base64,{img_b64}" alt="">'
        '<div class="dim"></div><div class="hud-grid"></div>'
        f'{HUD.format(state=state, time=time_text)}{laser}{extra}'
        '</div></div>'
    )


def card_html(result: dict | None, stats: dict) -> str:
    """Result panel: verdict card + key/value rows + session counters."""
    if result is None:
        head = (
            '<div class="verdict idle">'
            '<div class="top"><span class="sig"></span><span class="k">STANDBY</span></div>'
            '<div class="v">&mdash;</div>'
            '<div class="d">Waiting for a part photo.</div></div>'
        )
        kv = ""
    else:
        cls = result["cls"]
        extra = "" if cls == "ok" else " is-" + cls
        pct = result["confidence"] * 100.0
        head = (
            f'<div class="verdict{extra}">'
            f'<div class="top"><span class="sig"></span><span class="k">{result["verdict"]}</span></div>'
            f'<div class="v">{result["verdict"]}</div>'
            f'<div class="d">{result["desc"]}</div></div>'
        )
        kv = (
            '<div class="kv">'
            f'<div class="row"><span class="k">Confidence</span><span class="v">{pct:.1f}%</span></div>'
            f'<div class="row"><span class="k">Decision score</span>'
            f'<span class="meter{extra}"><i style="width:{pct:.0f}%"></i></span></div>'
            f'<div class="row"><span class="k">Cycle time</span><span class="v">{result["cycle"]:.2f} s</span></div>'
            '<div class="row"><span class="k">Engine</span><span class="v">v1.0</span></div>'
            '</div>'
        )

    summary = (
        '<div class="summary">'
        f'<div class="stat"><div class="n">{stats["total"]}</div><div class="l">Processed</div></div>'
        f'<div class="stat ok"><div class="n">{stats["pass"]}</div><div class="l">Pass</div></div>'
        f'<div class="stat bad"><div class="n">{stats["fail"]}</div><div class="l">Fail</div></div>'
        f'<div class="stat warn"><div class="n">{stats["review"]}</div><div class="l">Review</div></div>'
        '</div>'
    )
    return head + kv + summary


def log_html(rows: list[list]) -> str:
    """Inspection log rendered as a plain HTML table (full styling control)."""
    if not rows:
        body = ('<tr class="empty"><td colspan="6">No parts inspected yet.</td></tr>')
    else:
        cells = []
        for seq, name, verdict, conf, cycle, stamp in rows:
            cls = {"PASS": "ok", "FAIL": "bad"}.get(verdict, "warn")
            cells.append(
                f'<tr><td class="mono">{seq}</td><td class="mono">{name}</td>'
                f'<td><span class="tag {cls}">{verdict}</span></td>'
                f'<td class="mono">{conf}</td><td class="mono">{cycle}</td>'
                f'<td class="mono">{stamp}</td></tr>'
            )
        body = "".join(cells)
    return (
        '<div class="recess"><table class="log">'
        '<thead><tr><th>Seq</th><th>File</th><th>Result</th><th>Conf.</th>'
        '<th>Cycle</th><th>Timestamp</th></tr></thead>'
        f'<tbody>{body}</tbody></table></div>'
    )


CSS = """
:root{--laser:#4fe3ff}
body, .gradio-container{background:#0a0d12 !important}
.gradio-container{max-width:1040px !important; margin:0 auto !important; padding:14px 12px 28px !important;
  font:13px/1.5 "Segoe UI",system-ui,-apple-system,sans-serif !important; color:#e6edf6 !important}
footer{display:none !important}
.block, .form, .panel{background:transparent !important; border:0 !important; box-shadow:none !important}

/* ---- bezel / top bar ---- */
.bezel{display:flex;align-items:center;gap:13px;padding:9px 12px;border-radius:9px;
  background:linear-gradient(180deg,#1b222b,#12171d);border:1px solid #0b0f14;
  box-shadow:0 1px 0 rgba(255,255,255,.06) inset,0 6px 14px -8px #000}
.bezel .logo{display:flex;align-items:center;gap:9px}
.bezel .glyph{width:24px;height:24px;border-radius:5px;display:grid;place-items:center;
  background:linear-gradient(160deg,#3d7fd6,#1b3f74);box-shadow:0 1px 0 rgba(255,255,255,.25) inset}
.bezel b{font-size:13px}
.bezel span.sm{font-size:11px;color:#8695a8;margin-left:2px}
.sep{width:1px;height:20px;background:#0b0f14}
.lamp{display:flex;align-items:center;gap:6px;font-size:11px;color:#8695a8;letter-spacing:.04em}
.lamp i{width:7px;height:7px;border-radius:99px;background:#2b3441}
.lamp.on i{background:#35d07f;box-shadow:0 0 8px 1px rgba(53,208,127,.75)}
.lamp.cyan i{background:#4fe3ff;box-shadow:0 0 9px 2px rgba(79,227,255,.8)}
.lamp.amber i{background:#ffb020;box-shadow:0 0 8px 1px rgba(255,176,32,.7)}
.bezel .right{margin-left:auto;font:11px ui-monospace,Consolas,monospace;color:#7d8ea3}

/* ---- panels ---- */
.mods{display:grid;grid-template-columns:1.16fr 1fr;gap:12px;margin-top:12px}
@media(max-width:880px){.mods{grid-template-columns:1fr}}
.mod{border-radius:9px;background:linear-gradient(180deg,#141a21,#10151b);
  border:1px solid #1d242c;box-shadow:0 1px 0 rgba(255,255,255,.04) inset,0 10px 24px -18px #000;overflow:hidden}
.mod-head{display:flex;align-items:center;gap:8px;padding:8px 11px;border-bottom:1px solid #1d242c;
  background:linear-gradient(180deg,rgba(255,255,255,.03),rgba(255,255,255,0))}
.mod-head h2{margin:0;font:700 10.5px/1 "Segoe UI",sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#9fb0c4}
.mod-head .r{margin-left:auto;font:11px/1 ui-monospace,Consolas,monospace;color:#8695a8}

/* ---- viewport ---- */
.bezel-in{padding:9px;margin:10px;border-radius:10px;
  background:linear-gradient(180deg,#39434f,#1a2028 60%,#0e1217);
  box-shadow:0 1px 0 rgba(255,255,255,.14) inset,0 14px 30px -16px #000,0 2px 0 #090c10}
.screen{position:relative;border-radius:6px;overflow:hidden;background:#04070a;aspect-ratio:4/3;
  box-shadow:inset 0 0 70px rgba(0,0,0,.95),inset 0 0 0 1px #060a0f}
.screen img{width:100%;height:100%;object-fit:cover;display:block;opacity:.92;filter:saturate(.94) contrast(1.03)}
.screen .dim{position:absolute;inset:0;background:radial-gradient(circle at 50% 46%,rgba(0,0,0,0) 42%,rgba(0,0,0,.55) 100%)}
.hud-grid{position:absolute;inset:0;opacity:.20;pointer-events:none;
  background-image:linear-gradient(rgba(120,220,255,.22) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(120,220,255,.22) 1px,transparent 1px);
  background-size:34px 34px}
.br{position:absolute;width:22px;height:22px;border:2px solid rgba(79,227,255,.85);
  filter:drop-shadow(0 0 6px rgba(79,227,255,.65))}
.br.tl{top:10px;left:10px;border-right:0;border-bottom:0}
.br.tr{top:10px;right:10px;border-left:0;border-bottom:0}
.br.bl{bottom:10px;left:10px;border-right:0;border-top:0}
.br.br2{bottom:10px;right:10px;border-left:0;border-top:0}
.hud-tag{position:absolute;font:600 10px/1 ui-monospace,Consolas,monospace;letter-spacing:.08em;
  color:rgba(180,230,255,.82);text-shadow:0 0 8px rgba(0,0,0,.9)}
.hud-tag.tl{top:14px;left:40px}.hud-tag.tr{top:14px;right:40px;text-align:right}
.hud-tag.bl{bottom:14px;left:40px}.hud-tag.br2{bottom:14px;right:40px;text-align:right}

.laser,.trail,.scanline{position:absolute;left:0;right:0;pointer-events:none;opacity:0}
.laser{height:2px;background:linear-gradient(90deg,transparent,rgba(79,227,255,.9) 18%,#fff 50%,
  rgba(79,227,255,.9) 82%,transparent);box-shadow:0 0 22px 5px rgba(79,227,255,.55),0 0 60px 14px rgba(79,227,255,.22)}
.trail{height:130px;background:linear-gradient(to bottom,rgba(79,227,255,.20),rgba(79,227,255,.04) 55%,transparent)}
.scanline{inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.05) 0 1px,transparent 1px 3px);mix-blend-mode:overlay}
.scanning .laser,.scanning .trail,.scanning .scanline{opacity:1}
.scanning .laser{animation:sweep 1.15s cubic-bezier(.45,.05,.55,.95) 1 both}
.scanning .trail{animation:sweepTrail 1.15s cubic-bezier(.45,.05,.55,.95) 1 both}
.scanning .prog i{animation:progrow 1.15s linear 1 both}
@keyframes progrow{from{width:0%}to{width:100%}}
@keyframes sweep{from{top:-2px}to{top:100%}}
@keyframes sweepTrail{from{top:-130px}to{top:100%}}
.prog{position:absolute;left:12px;right:12px;bottom:38px;height:3px;background:rgba(255,255,255,.10);border-radius:99px;overflow:hidden}
.prog i{display:block;height:100%;background:linear-gradient(90deg,#2b9fd8,#4fe3ff);box-shadow:0 0 12px rgba(79,227,255,.8)}
.prog-text{position:absolute;left:12px;bottom:46px;font:600 10px/1 ui-monospace,Consolas,monospace;color:rgba(180,230,255,.85)}

.awaiting{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:7px}
.awaiting .aw-ico{font-size:26px;color:#2f3f52}
.awaiting .aw-1{font:700 11px/1 "Segoe UI",sans-serif;letter-spacing:.18em;color:#5d6f84}
.awaiting .aw-2{font-size:11.5px;color:#4d5c6e}

/* ---- result card ---- */
.readout{padding:11px}
.verdict{border-radius:8px;padding:12px 13px;border:1px solid rgba(53,208,127,.35);
  background:linear-gradient(180deg,rgba(53,208,127,.10),rgba(53,208,127,.03))}
.verdict .top{display:flex;align-items:center;gap:8px}
.verdict .sig{width:9px;height:9px;border-radius:99px;background:#35d07f;box-shadow:0 0 12px 2px rgba(53,208,127,.7)}
.verdict .k{font:700 10px/1 "Segoe UI",sans-serif;letter-spacing:.16em;text-transform:uppercase;color:#7fe0b0}
.verdict .v{font:700 30px/1.06 "Segoe UI",sans-serif;letter-spacing:-.6px;margin:9px 0 3px;color:#dffcec;
  text-shadow:0 0 22px rgba(53,208,127,.30)}
.verdict .d{font-size:11.5px;color:#9fdcbb;min-height:16px}
.verdict.is-bad{border-color:rgba(255,90,77,.42);background:linear-gradient(180deg,rgba(255,90,77,.12),rgba(255,90,77,.03))}
.verdict.is-bad .sig{background:#ff5a4d;box-shadow:0 0 12px 2px rgba(255,90,77,.7)}
.verdict.is-bad .k{color:#ff9d94}.verdict.is-bad .v{color:#ffe3e0}.verdict.is-bad .d{color:#f0b3ad}
.verdict.is-warn{border-color:rgba(255,176,32,.42);background:linear-gradient(180deg,rgba(255,176,32,.12),rgba(255,176,32,.03))}
.verdict.is-warn .sig{background:#ffb020;box-shadow:0 0 12px 2px rgba(255,176,32,.7)}
.verdict.is-warn .k{color:#ffcd7a}.verdict.is-warn .v{color:#fff0d2}.verdict.is-warn .d{color:#e8c48f}
.verdict.idle{border-color:#1d242c;background:#0d1218}
.verdict.idle .sig{background:#2b3441;box-shadow:none}
.verdict.idle .k{color:#6f7f92}.verdict.idle .v{color:#3f4c5c}.verdict.idle .d{color:#5a6a7d}

.kv{margin-top:10px;border:1px solid #1d242c;border-radius:7px;overflow:hidden;background:#0d1218}
.kv .row{display:flex;align-items:center;padding:7px 11px;border-bottom:1px solid #1d242c;font-size:12px}
.kv .row:last-child{border-bottom:0}
.kv .k{color:#8695a8;width:118px;flex:none}
.kv .v{margin-left:auto;font:600 12px/1.3 ui-monospace,Consolas,monospace;color:#d5e3f4}
.meter{height:5px;background:#1b232d;border-radius:99px;width:132px;overflow:hidden;margin-left:auto}
.meter i{display:block;height:100%;background:linear-gradient(90deg,#1f7a52,#35d07f);box-shadow:0 0 10px rgba(53,208,127,.6)}
.meter.is-bad i{background:linear-gradient(90deg,#8a2a24,#ff5a4d)}
.meter.is-warn i{background:linear-gradient(90deg,#8a6416,#ffb020)}

.summary{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:10px}
.stat{border:1px solid #1d242c;border-radius:6px;background:#0d1218;padding:8px 9px}
.stat .n{font:700 17px/1 ui-monospace,Consolas,monospace;letter-spacing:-.4px;color:#e8f3ff}
.stat .l{font:700 8.5px/1 "Segoe UI",sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#7d8ea3;margin-top:6px}
.stat.ok .n{color:#8ff0c0}.stat.bad .n{color:#ffb0a8}.stat.warn .n{color:#ffd79a}

/* ---- input + buttons ---- */
.io{padding:0 10px 11px}
.io img{border-radius:6px !important}
.scanbtn, .scanbtn button{width:100% !important;border:0 !important;border-radius:7px !important;cursor:pointer;
  padding:12px 14px !important;font:700 13px/1 "Segoe UI",sans-serif !important;letter-spacing:.06em !important;
  text-transform:uppercase !important;color:#02121a !important;
  background:linear-gradient(180deg,#7beaff,#3ccfe8 55%,#22a9c4) !important;
  box-shadow:0 1px 0 rgba(255,255,255,.5) inset,0 -2px 0 rgba(0,0,0,.25) inset,0 10px 24px -10px rgba(60,207,232,.65) !important}
.ghost, .ghost button{background:#111823 !important;border:1px solid #2b3540 !important;border-radius:5px !important;
  color:#a9bccf !important;font:600 10.5px/1 ui-monospace,Consolas,monospace !important;letter-spacing:.06em !important}

/* ---- dataframe ---- */
.logwrap{margin-top:12px}
.logwrap .recess{border-radius:8px;background:#0b0f14;border:1px solid #1d242c;
  box-shadow:inset 0 2px 10px rgba(0,0,0,.65);overflow:hidden}
table.dataframe, .table-wrap table{background:transparent !important;color:#b9c8da !important;font-size:11.5px !important}
table.dataframe thead th{background:#101620 !important;color:#7d8ea3 !important;
  font:700 9.5px/1 "Segoe UI",sans-serif !important;letter-spacing:.14em !important;text-transform:uppercase !important;
  border-color:#1d242c !important}
table.dataframe tbody td{border-color:#141b23 !important;font-family:ui-monospace,Consolas,monospace !important}


/* bezel text */
.bezel b{color:#eef5ff !important}
.bezel span.sm{color:#8fa0b4 !important}
.bezel .right{color:#8fa0b4 !important}
.bezel .lamp{color:#8695a8 !important}
/* readability + balanced columns */
.mod-head h2{color:#c9d8ea !important;opacity:1 !important}
.mod-head .r{color:#8fa0b4 !important}
.mods{align-items:stretch !important}
.mod{height:100%;display:flex;flex-direction:column}
.mod .io{margin-top:auto}


/* ---- inspection log table ---- */
.recess{border-radius:8px;background:#0b0f14;border:1px solid #1d242c;
  box-shadow:inset 0 2px 10px rgba(0,0,0,.65);overflow:hidden}
table.log{width:100%;border-collapse:collapse;font-size:11.5px}
table.log thead th{text-align:left;padding:8px 11px;background:#101620;color:#8ea1b6;
  font:700 9.5px/1 "Segoe UI",sans-serif;letter-spacing:.13em;text-transform:uppercase;
  border-bottom:1px solid #1d242c;white-space:nowrap}
table.log tbody td{padding:8px 11px;color:#c2d0e0;border-bottom:1px solid #141b23}
table.log tbody tr:nth-child(odd) td{background:#0d131a}
table.log tbody tr:last-child td{border-bottom:0}
table.log td.mono{font-family:ui-monospace,Consolas,monospace;font-variant-numeric:tabular-nums}
table.log tr.empty td{color:#5a6a7d;padding:16px 11px;text-align:center}
.tag{display:inline-block;font:700 9.5px/1 ui-monospace,Consolas,monospace;letter-spacing:.08em;
  padding:4px 7px;border-radius:3px;border:1px solid}
.tag.ok{color:#8ff0c0;border-color:rgba(53,208,127,.45);background:rgba(53,208,127,.10)}
.tag.bad{color:#ffb0a8;border-color:rgba(255,90,77,.45);background:rgba(255,90,77,.10)}
.tag.warn{color:#ffd79a;border-color:rgba(255,176,32,.45);background:rgba(255,176,32,.10)}

/* ---- Gradio internals overridden ---- */
/* dataframe: kill the white cell chrome */
.dataframe, .dataframe *{background-color:transparent !important;color:#b9c8da !important}
.table-wrap table, .table-container table{background:#0b0f14 !important}
.table-wrap thead th, .table-container thead th{background:#101620 !important;color:#8ea1b6 !important;
  font:700 9.5px/1 "Segoe UI",sans-serif !important;letter-spacing:.12em !important;text-transform:uppercase !important;
  border-bottom:1px solid #1d242c !important}
.table-wrap tbody td, .table-container tbody td{background:#0b0f14 !important;color:#c2d0e0 !important;
  border-bottom:1px solid #141b23 !important;font-family:ui-monospace,Consolas,monospace !important;font-size:11.5px !important}
.table-wrap tbody tr:nth-child(odd) td{background:#0d131a !important}
.cell-wrap, .cell-menu-wrap, .selection{background:transparent !important}
.header-row, .toolbar, .toolbar-buttons{background:transparent !important}
.icon-button{color:#7d8ea3 !important}

html, body, gradio-app, .gradio-container, .main, .wrap, .contain { background:#0a0d12 !important; color:#e6edf6 !important }
.gradio-container .prose :is(h1,h2,h3,h4,p,li,td,th){color:inherit !important}

/* image uploader */
.image-container{background:#0b0f14 !important;border:1px dashed #2f3a46 !important;border-radius:8px !important;
  box-shadow:none !important;min-height:150px !important}
.image-container .upload-container{background:transparent !important;color:#7d8ea3 !important}
.image-container .upload-container svg{color:#4a5a6d !important}
.icon-button-wrapper .icon-button, .icon-button{background:rgba(12,18,25,.86) !important;color:#a9bccf !important;
  border:1px solid #2b3540 !important;border-radius:4px !important;box-shadow:none !important}
.image-frame img{border-radius:6px !important}
.source-selection{color:#7d8ea3 !important}
.source-selection .icon{background:#111823 !important;border:1px solid #232c36 !important;border-radius:5px !important;color:#a9bccf !important}
.source-selection .icon.selected{border-color:#4fe3ff !important;color:#4fe3ff !important}

/* download button + dataframe + file */
.download-button, button.download-button{background:#111823 !important;border:1px solid #2b3540 !important;
  color:#a9bccf !important;border-radius:5px !important;font:600 10.5px/1 ui-monospace,Consolas,monospace !important;
  letter-spacing:.06em !important;padding:8px 12px !important;box-shadow:none !important}
.dataframe, .table-wrap, .table-container, .virtual-table-viewport{background:transparent !important}
.dataframe table{background:transparent !important}
.table-wrap{max-height:220px !important}
.table-container .header-row{background:#101620 !important;border-color:#1d242c !important}
.cell-wrap, .cell-menu-button{color:#b9c8da !important}
"""

HEADER_HTML = """
<div class="bezel">
  <div class="logo">
    <div class="glyph"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="#dceaf7"
      stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M4 8l8-4 8 4v8l-8 4-8-4V8z"/><path d="M4 8l8 4 8-4M12 12v8"/></svg></div>
    <div><b>PrintGuard</b><span class="sm">· IS-200</span></div>
  </div>
  <div class="sep"></div>
  <div class="lamp on"><i></i>POWER</div>
  <div class="lamp cyan"><i></i>SCAN</div>
  <div class="lamp"><i></i>ALERT</div>
  <div class="right">CAM-01 · 224×224 · ENGINE v1.0</div>
</div>
"""


# ---------------------------------------------------------------- app
def build_app(model: str, prefill: str | None = None):
    import gradio as gr

    stats: dict = {"total": 0, "pass": 0, "fail": 0, "review": 0}
    log_rows: list[list] = []

    def write_csv(rows: list[list]) -> str | None:
        if not rows:
            return None
        path = ROOT / "results" / "client_inspection_log.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["seq", "file", "result", "confidence", "cycle_s", "timestamp"])
            w.writerows(rows)
        return str(path)

    with gr.Blocks(title="PrintGuard · Inspection Station") as app:
        gr.HTML(f"<style>{CSS}</style>")
        gr.HTML(HEADER_HTML)

        state_log = gr.State([])

        with gr.Row(elem_classes=["mods"]):
            with gr.Column(elem_classes=["mod"]):
                gr.HTML('<div class="mod-head"><h2>Live View</h2>'
                        '<span class="r">CAM-01 · 224×224</span></div>')
                viewport = gr.HTML(viewport_html(None, "IDLE", "—"))
                with gr.Column(elem_classes=["io"]):
                    photo = gr.Image(type="pil", sources=["upload", "webcam"],
                                     label=None, show_label=False, height=150,
                                     value=prefill if prefill else None)
                    scan_btn = gr.Button("Scan part", elem_classes=["scanbtn"])

            with gr.Column(elem_classes=["mod"]):
                gr.HTML('<div class="mod-head"><h2>Inspection Result</h2>'
                        '<span class="r">LINE-A / ST-03</span></div>')
                card = gr.HTML(card_html(None, stats))

        with gr.Column(elem_classes=["logwrap"]):
            with gr.Row():
                gr.HTML('<div class="mod-head" style="border:0;background:none;flex:1">'
                        '<h2>Inspection Log</h2><span class="r">this session</span></div>')
                download = gr.DownloadButton("EXPORT CSV", value=None, elem_classes=["ghost"])
            table = gr.HTML(log_html([]))

        def inspect(image):
            if image is None:
                rows = list(log_rows)
                yield (viewport_html(None, "IDLE", "—"), card_html(None, stats),
                       log_html(rows), rows, write_csv(rows))
                return

            img_b64 = _b64(image)
            t_start = time.time()

            # frame 1: scanning (the CSS sweep takes SCAN_SECONDS)
            rows = list(log_rows)
            yield (viewport_html(img_b64, "SCANNING", "—", scanning=True, progress=0),
                   card_html(None, stats), log_html(rows), rows, write_csv(rows))

            result = predict(image, model)

            stats["total"] += 1
            key = {"PASS": "pass", "FAIL": "fail", "REVIEW": "review"}[result["verdict"]]
            stats[key] += 1

            stamp = datetime.now().strftime("%H:%M:%S")
            seq = len(log_rows) + 1
            log_rows.append([
                f"{seq:03d}", f"part_{seq:03d}.jpg", result["verdict"],
                f"{result['confidence'] * 100:.1f}%", f"{result['cycle']:.2f} s", stamp,
            ])
            rows = list(log_rows)

            time_left = SCAN_SECONDS - (time.time() - t_start)
            if time_left > 0:
                time.sleep(time_left)

            # frame 2: result
            yield (viewport_html(img_b64, "RESULT", f"{result['cycle']:.2f} s"),
                   card_html(result, stats), log_html(rows), rows, write_csv(rows))

        scan_btn.click(inspect, inputs=[photo],
                       outputs=[viewport, card, table, state_log, download])

    return app


# ---------------------------------------------------------------- cli
def main() -> None:
    ap = argparse.ArgumentParser(description="Client-facing inspection station.")
    ap.add_argument("--model", default=DEFAULT_MODEL,
                    help="backbone with a D1 checkpoint (vgg16 / resnet50 / mobilenet_v2 / xception / inception_resnet_v2)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=7861)
    ap.add_argument("--share", action="store_true")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--prefill", default=None, help="dev: initial image path")
    ap.add_argument("--selftest", action="store_true", help="run one inference and exit")
    args = ap.parse_args()

    if args.selftest:
        from PIL import Image

        sample = Path(args.prefill) if args.prefill else ROOT / "samples" / "D1_test" / "defect" / "IMG_9153.jpg"
        r = predict(Image.open(sample), args.model)
        print(f"[client] {sample.name} -> {r['verdict']}  P(defect)={r['p_defect']:.4f}  "
              f"conf={r['confidence'] * 100:.1f}%  cycle={r['cycle']:.2f}s  engine={r['model']}")
        return

    print(f"[client] engine = {args.model}__{DATASET}__{OPTIMIZER}__s{SEED}")
    app = build_app(args.model, args.prefill)
    app.launch(server_name=args.host, server_port=args.port,
               share=args.share, inbrowser=not args.no_browser, show_error=True,
               css=CSS)


if __name__ == "__main__":
    main()
