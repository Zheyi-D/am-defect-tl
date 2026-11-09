# 图表清单（报告用 · 单一权威版本）

> **报告里的图号以本文件为准。**
> `INDEX.md` 是 `analysis/make_figures.py` 自动生成的（只覆盖它生成的 5 张，内部编号 Figure 1–5
> 与报告图号不同）—— 写报告时用本文件，不要用 INDEX 的编号。

## 主图（报告正文用这 10 张）

| 报告图号 | 文件 | Caption (EN) | 用在哪节 | 生成方式 |
|---|---|---|---|---|
| Fig. 1 | `fig_pipeline.png` | Overview of the transfer-learning pipeline: frozen ImageNet backbone, paper-style head, and the 66-run matrix. | 2 | `python tools/make_pipeline_figure.py` |
| Fig. 2 | `fig_accuracy_by_model.png` | Test accuracy of eleven backbones on D1 and D2, with the values reported by Ahsan et al. overlaid. | 3.1 | `python -m analysis.make_figures` |
| Fig. 3 | `fig_optimizer_heatmap.png` | Effect of optimizer choice (Adam / SGD / RMSprop) on test accuracy, D1 (left) and D2 (right). | 3.2 | 同上 |
| Fig. 4 | `fig_confusion_grid.png` | Confusion matrices of the best and worst run on each dataset. | 3.1 | 同上 |
| Fig. 5 | `fig_delta_acc.png` | Accuracy difference between our reproduction and the reported values. | 3.3 | 同上 |
| Fig. 6 | `fig_ranking.png` | Backbones ranked by D1 test accuracy, annotated with the best optimizer. | 3.1 | 同上 |
| Fig. 7 | `fig_leakage_combined.png` | Leakage control experiment: random vs source-grouped split, two training-set regimes. | 3.4 | `python -m analysis.leakage --combine --out results` |
| Fig. 8 | `gradcam_vgg16__D1__adam__s42.png` | Grad-CAM visualisations for representative defect / non-defect samples. | 3.5 | `python -m analysis.gradcam --data-root ... --dataset D1` |
| Fig. 9 | `lime_vgg16__D1__adam__s42.png` | LIME super-pixel explanations for three checkpoints. | 3.5 | `python -m analysis.lime_explain --models ...` |
| Fig. 10 | `fig_efficiency.png` | Parameter count versus single-image latency (CPU). | 3.6 | `python -m analysis.efficiency` |

## 全部图文件（共 23 个 PNG，逐个列出，避免简写歧义）

| 文件 | 报告图号 | 用途 |
|---|---|---|
| `fig_accuracy_by_model.png` | Fig. 2 | main figure |
| `fig_confusion_grid.png` | Fig. 4 | main figure |
| `fig_delta_acc.png` | Fig. 5 | main figure |
| `fig_efficiency.png` | Fig. 10 | main figure |
| `fig_leakage_combined.png` | Fig. 7 | main figure |
| `fig_leakage_full.png` | — | leakage experiment, full-data regime only (backup) |
| `fig_leakage_small15.png` | — | leakage experiment, small-data regime only (backup) |
| `fig_optimizer_heatmap.png` | Fig. 3 | main figure |
| `fig_pipeline.png` | Fig. 1 | main figure |
| `fig_ranking.png` | Fig. 6 | main figure |
| `gradcam_inception_resnet_v2__D1__adam__s42.png` | — | Grad-CAM for another backbone (backup) |
| `gradcam_mobilenet_v2__D1__adam__s42.png` | — | Grad-CAM for another backbone (backup) |
| `gradcam_resnet50__D1__adam__s42.png` | — | Grad-CAM for another backbone (backup) |
| `gradcam_vgg16__D1__adam__s42.png` | Fig. 8 | main figure |
| `gradcam_xception__D1__adam__s42.png` | — | Grad-CAM for another backbone (backup) |
| `lime_mobilenet_v2__D1__adam__s42.png` | — | LIME for another backbone (backup) |
| `lime_resnet50__D1__adam__s42.png` | — | LIME for another backbone (backup) |
| `lime_vgg16__D1__adam__s42.png` | Fig. 9 | main figure |
| `predict_inception_resnet_v2__D1__adam__s42.png` | — | prediction grid incl. errors (backup / error analysis) |
| `predict_mobilenet_v2__D1__adam__s42.png` | — | prediction grid incl. errors (backup / error analysis) |
| `predict_resnet50__D1__adam__s42.png` | — | prediction grid incl. errors (backup / error analysis) |
| `predict_vgg16__D1__adam__s42.png` | — | prediction grid incl. errors (backup / error analysis) |
| `predict_xception__D1__adam__s42.png` | — | prediction grid incl. errors (backup / error analysis) |

## 表格（`reports/tables/`，脚本生成，禁止手改；共 6 张 × md + tex）

| 报告表号 | 文件 | Caption | 章节 |
|---|---|---|---|
| Table 1 | `table1_datasets.md` / `.tex` | Composition of the two public subsets. | 2.1 |
| Table 2 | `table2_d1_results.md` / `.tex` | Full results on D1 (11 × 3). | 3.1 |
| Table 3 | `table3_d2_results.md` / `.tex` | Full results on D2 (11 × 3). | 3.1 |
| Table 4 | `table4_delta.md` / `.tex` | Accuracy difference against the reported values. | 3.3 |
| Table 5 | `table5_efficiency.md` / `.tex` | Inference cost per image (params, FLOPs, CPU/GPU). | 3.6 |
| Table 6 | `table6_leakage.md` / `.tex` | Leakage control experiment on a re-augmented dataset (D2'): random split versus source-grouped split, under two training-set regimes. | 3.4 |
