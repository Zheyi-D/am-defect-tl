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

## 二、进行中：报告与口头演示（4 人写文档 + 2 人做 PPT/演示）

> 分工与取材说明见 [docs/START-HERE.md](docs/START-HERE.md)。写完请把自己的行补上。

| 代号 | 成员 | 负责 | 目标字数 | 状态 |
|---|---|---|---|---|
| **P1** | （姓名） | Abstract + §4 Conclusion & Recommendations + **统稿**（格式/页码/图表编号/字数/导出 docx） | 200 + 350 | ⬜ |
| **P2** | （姓名） | §1 Introduction（1.1–1.4）+ References（IEEE ≥15，含正文 in-text 引用） | 600 | ⬜ |
| **P3** | （姓名） | §2 Project Description（2.1–2.4，含 Algorithm 1 伪代码 + Fig. 1） | 1,000 | ⬜ |
| **P4** | （姓名） | §3 Results and Discussion（3.1–3.6）+ 全部图表排版（Fig. 1–10、Table 1–6） | 1,400 | ⬜ |
| **S1** | （姓名） | 15 页 PPT 内容 + 每页讲稿/时间分配 + 彩排计时（≤15:00） | — | ⬜ |
| **S2** | （姓名） | 现场 demo 操作 + 90 秒录屏 `demo_fallback.mp4` + 断网预案 + Q&A 卡片 | — | ⬜ |

**全员**：各写 1 份个人贡献报告（300–600 词），并参与彩排与口头问答。

## 三、用法

1. 每完成一块，在自己那一行补上**具体做了什么**（不要写"参与了讨论"这种无法验证的描述）
2. 写个人贡献报告时按：**我负责什么 → 我具体做了哪些决定/实现 → 我遇到的最大问题及解决方式 → 我学到什么**
3. 数字与证据优先引用：commit 哈希、PR 编号、`results/leaderboard.csv`、`results/figures/CATALOG.md`
