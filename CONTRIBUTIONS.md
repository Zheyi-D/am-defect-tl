# 贡献记录（个人贡献报告的唯一素材来源）

> 写个人贡献报告（300–600 词）时按这张表展开：**负责什么 → 具体做了什么 → 遇到什么问题怎么解决 → 学到什么**。
> 期末这份表也是"谁真的干了活"的客观证据。
> 代码部分的证据都可以在 git 历史里查到（提交哈希 / PR #8）。

---

## 一、已完成：代码与实验（2026-10-22 → 11-09）

| 成员 | 负责范围 | 具体产出 | 证据 |
|---|---|---|---|
| **Kenneth**（GitHub `Zheyi-D`） | 训练管线与全部 GPU 实验 | `src/` 10 个模块（数据定位/缓存/划分/模型/训练/批跑/汇总/评估）；66 个正式 run；10 个分类头 checkpoint；泄漏对照实验（D2′ 自建增强 + 双划分，12 run）；GPU 时延测量；仓库结构与文档 | commits `e47e2c6`、`1b44b5f`、`8d6b3c9`、`fcf2373`、`0cbea0b`、`b5b99e5` |
| **jellyfishhamburger**（GitHub `jellyfishhamburger`） | 图表 / 表格 / 效率 / 解释性 / demo / 工程收尾（T1–T6，无需 GPU） | `analysis/make_figures.py`（6 图 + 索引）；`export_tables.py`（5 表 × md/tex，448 个数值逐格核对）；`efficiency.py`（11 骨干参数量/FLOPs/CPU 时延）；`lime_explain.py`（3 张 LIME）；`demo_app.py` + `checkpoint.py`（Gradio demo + 结果看板）；`reproduce.sh`、`tests/test_analysis_outputs.py`、`docs/archive/`、清理死代码 | **PR #8**（16 commits，2026-11-09 合并，`4f11d80`） |

### 代码模块 → 作者

| 模块 | 作者 | 说明 |
|---|---|---|
| `src/locate_data.py` · `data_prepare.py` · `splits.py` · `dataset.py` | Kenneth | 数据定位、224 缓存、冻结划分、读图 |
| `src/models.py` · `train.py` · `batch.py` · `aggregate.py` · `evaluate.py` | Kenneth | 11 骨干 + 冻结 + 论文同款头；单 run / 66 矩阵 / 汇总 / 10 指标 |
| `analysis/leakage.py` | Kenneth | 泄漏对照实验（**自主贡献**） |
| `analysis/gradcam.py` | Kenneth | Grad-CAM + 预测示例图 |
| `analysis/make_figures.py` · `export_tables.py` | jellyfishhamburger | 报告图 / 表生成（T1、T2） |
| `analysis/efficiency.py` | jellyfishhamburger | 参数量 / FLOPs / CPU 时延（T3，GPU 列由 Kenneth 补） |
| `analysis/lime_explain.py` · `demo_app.py` · `checkpoint.py` | jellyfishhamburger | LIME（T4）、Gradio demo（T5） |
| `tools/build_kernel.py` · `fetch_paper_results.py` · `measure_gpu_latency.py` | Kenneth | Kaggle 自包含 kernel、作者结果表抽取、GPU 时延 |
| `tools/build_report_docx.py` | Kenneth | 报告骨架 docx（封面 + 标题） |
| `reproduce.sh` · `tests/test_analysis_outputs.py` | jellyfishhamburger | 一键复现、分析产物测试（T6） |
| `tests/test_contracts.py` | Kenneth | 契约测试（划分不泄漏 / metrics schema） |

> 已删除：`src/features.py`（特征缓存方案，实际改用图片缓存后不再需要，T6 清理）。

---

## 二、进行中：报告与口头演示（其余 6 位成员）

> 以下由报告组同学自行填写；负责人代号见 `reports/WPS-REPORT-OUTLINE.md` 的目录表。

| 成员 | 负责章节 / 任务 | 目标字数 | 状态 | 备注 |
|---|---|---|---|---|
| （姓名） | Abstract + 第 4 节 Conclusion + 统稿 | 200 + 350 | ⬜ | |
| （姓名） | 第 1 节 Introduction + References | 600 | ⬜ | IEEE ≥15 条 |
| （姓名） | 第 2 节 Project Description | 1,000 | ⬜ | |
| （姓名） | 第 3.1–3.3（对比 / 消融 / 与论文异同）+ 全部表格 | 900 | ⬜ | |
| （姓名） | 第 3.4–3.6（泄漏 / 可解释性 / 效率）+ 全部图排版 | 500 | ⬜ | |
| （姓名） | PPT（15 页）+ 彩排计时 + 口头分段 | — | ⬜ | |
| （姓名） | 个人贡献报告收集 + 参考文献格式检查 | — | ⬜ | |

---

## 三、用法

1. 每完成一块，在自己那一行补上**具体做了什么**（不要写"参与了讨论"这种无法验证的描述）
2. 写个人贡献报告时按：**我负责什么 → 我具体做了哪些决定/实现 → 我遇到的最大问题及解决方式 → 我学到什么**
3. 数字与证据优先引用：commit 哈希、PR 编号、`results/leaderboard.csv`、`results/figures/CATALOG.md`
