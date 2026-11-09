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

## 备用图（可放附录，或按需替换主图）

| 文件 | 说明 |
|---|---|
| `gradcam_{resnet50,mobilenet_v2,xception,inception_resnet_v2}__D1__adam__s42.png` | 其余 4 个模型的 Grad-CAM |
| `predict_*__D1__adam__s42.png`（5 张） | 预测结果网格（含错例），适合做错误分析插图 |
| `lime_{resnet50,mobilenet_v2}__D1__adam__s42.png` | 另外 2 个模型的 LIME |
| `fig_leakage_full.png` / `fig_leakage_small15.png` | 泄漏实验的单设定版本（主图用 combined） |
| `fig_confusion_grid.png` | 已用作 Fig. 4 |

## 表格（`reports/tables/`，脚本生成，禁止手改；共 6 张 × md + tex）

| 报告表号 | 文件 | Caption | 章节 |
|---|---|---|---|
| Table 1 | `table1_datasets.md` / `.tex` | Composition of the two public subsets. | 2.1 |
| Table 2 | `table2_d1_results.md` / `.tex` | Full results on D1 (11 × 3). | 3.1 |
| Table 3 | `table3_d2_results.md` / `.tex` | Full results on D2 (11 × 3). | 3.1 |
| Table 4 | `table4_delta.md` / `.tex` | Accuracy difference against the reported values. | 3.3 |
| Table 5 | `table5_efficiency.md` / `.tex` | Inference cost per image (params, FLOPs, CPU/GPU). | 3.6 |
| Table 6 | `table6_leakage.md` / `.tex` | Leakage control experiment on a re-augmented dataset (D2'): random split versus source-grouped split, under two training-set regimes. | 3.4 |
