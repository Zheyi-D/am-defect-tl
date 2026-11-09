# 报告草稿（6 人共写区）

> 规则：在**你负责的那节标题**下面写，不要删改别人的段落。
> 数字只能来自 `results/leaderboard.csv` / `reports/tables/`；图用图号引用，见 `results/figures/CATALOG.md`。
> 正式版在金山文档里，这里是草稿与备份。目标总字数 ≈ 3,550（上限 4,400）。

---

## Abstract

<!-- 约 200 词：任务是什么、用什么方法、覆盖 66/99、主要发现三条 -->


## 1 Introduction

<!-- 约 600 词，官方要求四个子问题都要答 -->

### 1.1 Motivation

<!-- 约 200 词：为什么 3D 打印件需要自动缺陷检测 -->


### 1.2 Objectives

<!-- 约 150 词：我们要复现什么、要额外做什么 -->


### 1.3 Background

<!-- 约 150 词：AMdataset、D1/D2 是什么、论文做了什么 -->


### 1.4 Tools and Environment

<!-- 约 100 词：PyTorch + timm + scikit-learn、Kaggle T4、冻结骨干策略 -->


## 2 Project Description

<!-- 约 1,000 词；含 Fig. 1（fig_pipeline.png）与 Algorithm 1 -->

### 2.1 Main Objectives

<!-- 约 150 词：复现 11×3×2 矩阵 + 4 项自主分析 -->


### 2.2 Dataset and Problem Formulation

<!-- 约 300 词：D1 271 张（136/135）、D2 3017 张（947/2070）、70/10/20、positive = defect、Table 1 -->


### 2.3 Techniques and Algorithms

<!-- 约 400 词：迁移学习原理、11 个骨干、论文同款分类头、优化器；此处插入 Algorithm 1
     （伪代码原文见 reports/WPS-REPORT-OUTLINE.md §九，直接复制） -->


### 2.4 Training Protocol and Evaluation Metrics

<!-- 约 150 词：head-only 训练、超参、10 个指标、混淆矩阵定义 -->


## 3 Results and Discussion

<!-- 约 1,400 词；Fig. 2–10，Table 2–6。三条必须写对：
     ① EfficientNet 在论文里 F1=0（塌成多数类），不是我们更强；
     ② 泄漏实验是阴性结论（|Δ|≤1.5%，多数为负）；
     ③ D1 测试集仅 54 张，0.02 差距无统计意义。 -->

### 3.1 Overall Model Comparison

<!-- 约 350 词：Fig. 2 准确率对比、Fig. 6 排名、Fig. 4 混淆矩阵、Table 2–3 -->


### 3.2 Optimizer Ablation

<!-- 约 250 词：Fig. 3 热力图；Adam 最稳，骨干排序不随优化器变 -->


### 3.3 Comparison with the Reported Results

<!-- 约 300 词：Fig. 5 Δacc、Table 4；EfficientNet 家族差异的真实原因（/255 归一化） -->


### 3.4 Data-Leakage Control Experiment

<!-- 约 250 词：自建 D2′ 保留溯源、随机 vs 分组划分、两种训练集规模、结论为阴性；Fig. 7 + Table 6 -->


### 3.5 Explainability: Grad-CAM and LIME

<!-- 约 150 词：Fig. 8–9；红区落在试样上而非背景；失败案例集中在细杆/低对比 -->


### 3.6 Deployment Cost

<!-- 约 100 词：Fig. 10 + Table 5；T4 上全部 ≤40 ms；CPU 上只有 MobileNetV2 / EfficientNet-B0 满足实时 -->


## 4 Conclusion and Recommendations

<!-- 约 350 词：结论三条 + 建议（轻量模型 + CPU 方案）+ 限制（第三数据集未公开、D2 非独立） -->


## References

<!-- IEEE 格式，≥15 条；正文必须有 in-text 引用如 [1]。
     起始 10 条见 reports/WPS-REPORT-OUTLINE.md §六 -->


## 附录：PPT 与演示（S1 / S2 用）

> 这部分不是报告正文，是口头报告的草稿区。

### Slide outline（15 页）

<!-- 每页：标题 + 3–5 个要点；按 结果逻辑 排：问题→数据→方法→结果→分析→结论 -->


### Speaker notes（分段与时间）

<!-- 8 人各 60–90 秒；总 15:00；Q&A 5:00 -->


### Demo recording notes

<!-- 文件名 demo_fallback.mp4（视频不进仓库，只写存放位置与时长）
     录制步骤见 docs/DEMO.md §9 -->


### Q&A cards

<!-- 预判 10 个问题；参考 docs/DEMO.md §6 的 8 个现成答案 -->
