# WPS 共享文档：封面 + 目录（源文件）

> 🔗 **在线文档（实际协同编辑的地方）：https://www.kdocs.cn/l/cokbmUbGMYkE**
> 入口与权限说明见 [ONLINE.md](ONLINE.md)。
>
> **这份文件是 Kdocs/WPS 共享报告的"骨架源"**：封面与目录在这里定稿、进 Git 版本管理，
> 实际文档在金山文档里协同编辑。
> 同步规则：改结构 → 改这里并提 PR；只改文字 → 直接在金山文档改。
>
> 相关文件：[reports/README.md](README.md)（归档约定）、[docs/SUBMISSION.md](../docs/SUBMISSION.md)（提交清单）、
> [results/figures/CATALOG.md](../results/figures/CATALOG.md)（图号与 caption 的单一权威版本）。

---

# 一、封面（直接照抄进文档首页）

```text
================================================================
                    IDAT7215 Computer Programming
             for Product Development and Applications

              Python-Based Transfer Learning for
            3D Printed Object Defect Detection

        A Reproducibility Study of Ahsan et al. (2024)


                    Group Project (25%)

    Group No.:            <组号>
    Programme / Class:    <班级>

    Members (Name — UID):
      1. <姓名>  <UID>
      2. <姓名>  <UID>
      3. <姓名>  <UID>
      4. <姓名>  <UID>
      5. <姓名>  <UID>
      6. <姓名>  <UID>
      7. <姓名>  <UID>
      8. <姓名>  <UID>

    Group Leader:         <姓名>

    Word Count (body):    <数字>   ≈ 3,550（目标 2,000–4,000，上限 4,400）

    Date of Submission:   <2026-11-30>

    Repository: https://github.com/Zheyi-D/am-defect-tl
================================================================
```

> 封面单独一页，不编页码；正文从 Abstract 之后开始编页。

---

# 二、目录（Table of Contents）

> 结构按官方《Group Project Guidelines》第 1–4 节的必答项对齐（1.1–1.4 / 2.1–2.4 / 结论含建议）。

| 章节 | 内容 | 目标字数 | 图表 | 负责人 |
|---|---|---|---|---|
| — | Cover page（课程/班级/组号/姓名学号/字数） | — | — | 统稿 |
| — | Table of Contents | — | — | 统稿 |
| — | Abstract | 200 | — | 统稿 |
| — | List of Figures / List of Tables | — | — | 统稿 |
| **1** | **Introduction** | 600 | — | B |
| 1.1 | Motivation（研究动机） | 200 | — | B |
| 1.2 | Objectives（项目目的） | 150 | — | B |
| 1.3 | Background（项目背景） | 150 | — | B |
| 1.4 | Tools and Environment（工具） | 100 | — | B |
| **2** | **Project Description** | 1,000 | Fig. 1, Table 1, Algorithm 1 | C |
| 2.1 | Main Objectives | 150 | — | C |
| 2.2 | Dataset and Problem Formulation | 300 | Table 1 | C |
| 2.3 | Techniques and Algorithms（含**伪代码 Algorithm 1**） | 400 | Algorithm 1 | C |
| 2.4 | Training Protocol and Evaluation Metrics | 150 | — | C |
| **3** | **Results and Discussion** | 1,400 | Fig. 2–10, Table 2–6 | D + E |
| 3.1 | Overall Model Comparison | 350 | Fig. 2, 4, 6；Table 2–3 | D |
| 3.2 | Optimizer Ablation | 250 | Fig. 3 | D |
| 3.3 | Comparison with the Reported Results | 300 | Fig. 5；Table 4 | D |
| 3.4 | Data-Leakage Control Experiment（自主贡献） | 250 | Fig. 7；Table 6 | E |
| 3.5 | Explainability: Grad-CAM and LIME | 150 | Fig. 8–9 | E |
| 3.6 | Deployment Cost | 100 | Fig. 10；Table 5 | E |
| **4** | **Conclusion and Recommendations** | 350 | — | 统稿 |
| — | Individual Contributions（8 × 300–600 词） | 不计入 | — | 全员 |
| — | References（IEEE ≥15，正文需有 in-text 引用） | 不计入 | — | B |
| — | Appendix A：完整 66 结果表 | 不计入 | Table A1 | D |
| — | Appendix B：复现命令与环境 | 不计入 | — | Kenneth |

**字数合计（计入部分）**：200 + 600 + 1,000 + 1,400 + 350 = **3,550 词**

---

# 三、图表清单（编号固定，勿改）

## Figures

> 图号以 [`results/figures/CATALOG.md`](../results/figures/CATALOG.md) 为准（含 5 张备用图）。

| 编号 | 文件 | Caption（英文，可直接用） | 章节 |
|---|---|---|---|
| Fig. 1 | `results/figures/fig_pipeline.png` ⚠️**待生成** | Overview of the transfer-learning pipeline: frozen backbone, paper-style head, and the 66-run matrix. | 2 |
| Fig. 2 | `fig_accuracy_by_model.png` | Test accuracy of eleven backbones on D1 and D2, with reported values overlaid. | 3.1 |
| Fig. 3 | `fig_optimizer_heatmap.png` | Effect of optimizer choice on test accuracy, D1 (left) and D2 (right). | 3.2 |
| Fig. 4 | `fig_confusion_grid.png` | Confusion matrices of the best and worst run per dataset. | 3.1 |
| Fig. 5 | `fig_delta_acc.png` | Accuracy difference between our reproduction and the reported values. | 3.3 |
| Fig. 6 | `fig_ranking.png` | Backbones ranked by D1 test accuracy, annotated with the best optimizer. | 3.1 |
| Fig. 7 | `fig_leakage_combined.png` | Leakage control experiment: random vs source-grouped split, two training regimes. | 3.4 |
| Fig. 8 | `gradcam_vgg16__D1__adam__s42.png` | Grad-CAM visualisations for representative samples. | 3.5 |
| Fig. 9 | `lime_vgg16__D1__adam__s42.png` | LIME super-pixel explanations for three checkpoints. | 3.5 |
| Fig. 10 | `fig_efficiency.png` | Parameter count versus single-image latency. | 3.6 |

## Tables

| 编号 | 文件 | Caption | 章节 |
|---|---|---|---|
| Table 1 | `reports/tables/table1_datasets.md` | Composition of the two public subsets of the AMdataset. | 2.1 |
| Table 2 | `table2_d1_results.md` | Full results on D1: 11 backbones × 3 optimizers (10 metrics each). | 3.1 |
| Table 3 | `table3_d2_results.md` | Full results on D2: 11 backbones × 3 optimizers (10 metrics each). | 3.1 |
| Table 4 | `table4_delta.md` | Accuracy difference against the reported values, aggregated per backbone. | 3.3 |
| Table 5 | `table5_efficiency.md` | Inference cost per image (params, FLOPs, CPU and GPU latency). | 3.6 |
| Table 6 | **待生成**：`results/leakage.csv` 转表 | Leakage control experiment: random versus source-grouped split. | 3.4 |

---

# 四、三个必须写进去的结论（不许改数字）

1. **模型排序基本复现**：Xception / MobileNetV2 / InceptionResNetV2 与论文差 ≤ 0.02。
2. **EfficientNet 家族在论文中失效**（D1 上 F1 = 0），我们正常收敛到 0.98–1.00；
   最可能原因是作者对所有骨干统一使用 `/255` 归一化，而 EfficientNet 需要自带的 `preprocess_input`。
3. **泄漏对照实验为阴性**：两套划分准确率差 \|Δ\| ≤ 1.5% 且多数为负 → 高准确率主要来自任务区分度高，
   不能归因于数据泄漏（见 `results/leakage.csv`）。

补充（3.6 用）：
> T4 上 11 个模型全部 ≤ 40 ms/张；纯 CPU 上只有 MobileNetV2（22.9 ms，≈44 FPS）和
> EfficientNet-B0（34.6 ms，≈29 FPS）满足实时质检 → **模型选型取决于部署硬件**。

---

# 五、格式规范（导出前逐条核对）

| 项 | 要求 |
|---|---|
| 纸张 / 页边距 | A4，默认页边距（上下 2.54 cm，左右 3.17 cm） |
| 字体 | 正文 Times New Roman 12 pt |
| 行距 | 单倍（Single） |
| 段后间距 | 6 pt，段首不缩进（或统一缩进 2 字符，全文一致） |
| 标题层级 | H1 16 pt 粗体 / H2 14 pt 粗体 / H3 12 pt 粗体 |
| 图 | 居中，图注在图下方，9–10 pt，编号 `Fig. 1` |
| 表 | 三线表（booktabs 风格），表注在表上方，9–10 pt |
| 页码 | 右下角，封面不编号 |
| 引用 | IEEE 数字方括号 `[1]`，References 单独起页 |

---

# 六、References 起始清单（IEEE，B 同学补齐到 ≥15 条）

```text
[1] M. M. Ahsan, S. Raman, Y. Liu, and Z. Siddique, "Defect analysis of 3D printed object using
    transfer learning approaches," Expert Systems with Applications, vol. 253, p. 124293, Nov. 2024,
    doi: 10.1016/j.eswa.2024.124293.
[2] C. L. Chen et al., "AMdataset: additive manufacturing image dataset," University of Oklahoma,
    2024. [Online]. Available: https://github.com/mahsan2/AMdataset
[3] K. He, X. Zhang, S. Ren, and J. Sun, "Deep residual learning for image recognition," in Proc.
    IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), 2016, pp. 770–778.
[4] K. Simonyan and A. Zisserman, "Very deep convolutional networks for large-scale image
    recognition," in Proc. Int. Conf. Learn. Represent. (ICLR), 2015.
[5] M. Tan and Q. Le, "EfficientNet: Rethinking model scaling for convolutional neural networks,"
    in Proc. Int. Conf. Mach. Learn. (ICML), 2019, pp. 6105–6114.
[6] A. G. Howard et al., "MobileNets: Efficient convolutional neural networks for mobile vision
    applications," arXiv:1704.04861, 2017.
[7] F. Chollet, "Xception: Deep learning with depthwise separable convolutions," in Proc. CVPR,
    2017, pp. 1251–1258.
[8] R. R. Selvaraju et al., "Grad-CAM: Visual explanations from deep networks via gradient-based
    localization," in Proc. IEEE Int. Conf. Comput. Vis. (ICCV), 2017, pp. 618–626.
[9] M. T. Ribeiro, S. Singh, and C. Guestrin, "'Why should I trust you?': Explaining the
    predictions of any classifier," in Proc. ACM SIGKDD, 2016, pp. 1135–1144.
[10] A. Paszke et al., "PyTorch: An imperative style, high-performance deep learning library,"
     in Proc. NeurIPS, 2019, pp. 8024–8035.
```

---

# 七、当前缺口（写之前要先补的）

| # | 缺什么 | 谁补 | 影响 |
|---|---|---|---|
| 1 | **Fig. 1 方法流程图**（`fig_pipeline.png`） | 待定（可用 matplotlib/PowerPoint 画） | 第 2 节需要 |
| 2 | **Table 6 泄漏实验表**（`results/leakage.csv` → md） | 待定（`export_tables.py` 加一节即可） | 3.4 需要 |
| 3 | **封面成员名单 / 组号 / 班级** | 组长 | 封面占位符 |
| 4 | **数据集示例图**（可选，D1 缺陷 vs 无缺陷各 2 张） | 待定 | 2.1 会更好读 |

---

# 八、同步到金山文档的流程

1. 我在金山文档建 **Word (.docx)** 类型文档，标题 `IDAT7215 Topic4 Report`
2. 把本文件的"封面"+"目录"+"图表清单"写进去（作为文档骨架）
3. 生成分享链接（可编辑）→ 发群
4. 8 人在线分工填写；每次结构变动回改本文件并提 PR
5. 定稿：从金山文档导出 docx → 存 `reports/submission/`
