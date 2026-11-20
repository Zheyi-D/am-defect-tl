> 需要先理解全貌？读 [WALKTHROUGH.md](WALKTHROUGH.md)（从 0 到 1，含每一步的命令与产物）。

# START HERE —— 写报告 / 做 PPT / 录演示的同学先看这个

> **你是 AI agent 吗？** 把本文件从头读到尾再动手。仓库里所有数字、图、表都已就绪，
> 你的任务**不是**重新计算或重新跑实验，而是**按结构把内容写出来**。

---

## 0. 一句话背景

11 个 ImageNet 预训练骨干（冻结卷积、只训新分类头）× 3 种优化器 × 2 个数据集 = **66 个 run**，
全部跑完并与论文 Ahsan et al. (2024) 逐格对比；另有 4 项自主分析（泄漏对照、Grad-CAM、LIME、部署效率）。

- 代码与实验：已完成，**不要改**
- 报告正文：https://www.kdocs.cn/l/cokbmUbGMYkE （只有封面 + 标题，正文留空）
- 幻灯片：https://www.kdocs.cn/l/co7EkTOqxwN0 （15 页骨架）

---

## 1. 分工（4 人文档 + 2 人 PPT/演示）

| 代号 | 负责内容 | 参考字数 | 交付位置 |
|---|---|---|---|
| **P1** | Abstract + §4 Conclusion & Recommendations + **统稿**（格式、页码、图表编号、字数、导出 docx） | 200 + 350 | 在线文档 |
| **P2** | §1 Introduction（1.1 Motivation / 1.2 Objectives / 1.3 Background / 1.4 Tools）+ **References（IEEE ≥15，正文要有 in-text 引用）** | 600 | 在线文档 |
| **P3** | §2 Project Description（2.1–2.4，含 **Algorithm 1 伪代码** 与 Fig. 1） | 1,000 | 在线文档 |
| **P4** | §3 Results and Discussion（3.1–3.6）+ **全部图表排版**（Fig. 1–10、Table 1–6） | 1,400 | 在线文档 |
| **S1** | **15 页 PPT** 内容 + 每页讲稿/时间分配 + 彩排计时（≤15:00） | — | 在线 PPT |
| **S2** | **现场 demo 操作 + 90 秒录屏**（`demo_fallback.mp4`）+ 断网预案 + Q&A 卡片 | — | 录屏文件 + PPT 备注 |

> **各节字数和总字数都只是建议分配，不是硬性规定** —— 按实际内容需要调整即可。
> 官方唯一的硬性要求：正文总量在 **2,000–4,000 词**之间（+10% 容差即 ≤4,400，超出扣 10%）。
> 我们默认按 ≈3,500 词分配，觉得某节该多写就多写，只要整体落在范围内。
> 每节字数见 [reports/WPS-REPORT-OUTLINE.md](../reports/WPS-REPORT-OUTLINE.md) 的目录表。

---

## 2. 三条铁律（违反必扣分）

1. **数字只认仓库**：`results/leaderboard.csv`、`reports/tables/table*.md`、`results/leakage.csv`、`results/efficiency.csv`。
   **不许自己算、不许估、不许"补一个看起来合理的数"**。查不到就说查不到。
2. **不要改代码和结果**：`src/`、`analysis/`、`results/`、`splits/` 一律不动。
   要改文字 → 只改在线文档；要改结构 → 先在群里问。
3. **不确定就写不确定**：比如"测试集只有 54 张，0.98 与 1.00 的差别不具统计意义" —— 这种诚实的表述是加分项。

---

## 3. 取材路由（我需要什么 → 去哪拿）

| 你需要 | 直接去这里 |
|---|---|
| **所有数字 / 10 个指标 / 66 行结果** | [`results/leaderboard.csv`](../results/leaderboard.csv) |
| 论文报告值（作者原始 99 格） | [`docs/paper_results.csv`](../docs/paper_results.csv) |
| **报告表格（可直接粘）** | [`reports/tables/`](../reports/tables/) — `table1…table6` × `.md` / `.tex` |
| **图的清单 + 英文 caption + 用在哪节** | [`results/figures/CATALOG.md`](../results/figures/CATALOG.md) ← **以这个为准** |
| 图文件本身 | `results/figures/*.png` |
| 数据集细节（张数、划分、来源） | [`docs/DATA.md`](../docs/DATA.md) |
| 论文方法 vs 我们实现差异 | [`docs/AUTHOR_CODE.md`](../docs/AUTHOR_CODE.md) |
| 结果字段定义 | [`docs/RESULTS.md`](../docs/RESULTS.md) |
| **Method 流程图（Fig. 1）** | `results/figures/fig_pipeline.png` |
| **伪代码（第 2 节用）** | [outline §九](../reports/WPS-REPORT-OUTLINE.md) 里的 Algorithm 1，直接复制 |
| 效率数据（CPU/GPU 时延） | [`results/efficiency.csv`](../results/efficiency.csv) |
| 泄漏对照实验 | [`results/leakage.csv`](../results/leakage.csv) + `Table 6` |
| **提交要求 / 格式 / 检查清单** | [`docs/SUBMISSION.md`](SUBMISSION.md) |
| **demo 与录屏步骤** | [`docs/DEMO.md`](DEMO.md) |
| 引用信息（论文 DOI、数据来源） | [`README.md` §7](../README.md) |
| 开源组件登记（写"哪些代码是自研"） | [`NOTICE.md`](../NOTICE.md) |

---

## 4. 六个最容易写错的事实（自查用）

| # | 正确表述 | 常见错误 |
|---|---|---|
| 1 | 11 骨干 × 3 优化器 × 2 数据集 = **66** 个 run | 写成 99 / 33 |
| 2 | 论文是 **99** 格，第三个数据集（1,557 张）未公开 → 我们覆盖 **66/99** | 说"我们复现了全部 99 个" |
| 3 | **D2 是 D1 的数据增强版**，不是独立采集 | 说"两个独立数据集" |
| 4 | EfficientNet 家族在论文里 **F1 = 0（塌成多数类）**，我们正常收敛 → 那三行 +0.49 的差距**不是**我们更强 | 写成"我们显著超过论文" |
| 5 | **泄漏对照实验是阴性结论**：随机划分 vs 按原图分组划分，准确率差 \|Δ\| ≤ 1.5% 且多数为负 → **高准确率来自任务本身容易，不能归因于泄漏** | 写成"我们证明了数据泄漏"（旧稿的说法，已作废） |
| 6 | D1 测试集只有 **54 张**：错 1 张 = 1.8 个百分点，0.98 与 1.00 的差别**不具统计意义** | 拿 0.02 的差距下强结论 |

> 额外：部署结论是"**模型选型取决于硬件**"——T4 上 11 个模型全部 ≤40 ms；
> 纯 CPU 上只有 MobileNetV2（22.9 ms）与 EfficientNet-B0（34.6 ms）满足实时。

---

## 5. 给 AI 的提示词（直接复制）

```text
你要帮我写 IDAT7215 小组报告的 <第 X 节 / 某小节>。

先读这三个文件（按顺序）：
1. docs/START-HERE.md      —— 分工、铁律、取材路由
2. reports/WPS-REPORT-OUTLINE.md —— 目录、字数、各节要点、Algorithm 1
3. results/figures/CATALOG.md    —— 图号与英文 caption

硬性要求：
- 所有数字必须来自 results/leaderboard.csv 或 reports/tables/；查不到就写 "not available"，不要估算。
- 图号一律用 CATALOG.md 里的 Fig. N；表号用 Table N。
- 英文写作，学术语气，不用 emoji，不用第一人称复数以外的花哨表达。
- 长度参考：<参考字数> 词左右即可，可多可少，以把问题说清为准。
- 写完在末尾列出你引用过的数字及其来源文件（便于我核对）。
```

---

## 6. 写作流程（每个 P）

1. 打开在线文档，找到自己的标题，在下面直接写（不要改别人的段落）
2. 写完自查第 4 节的 6 条事实
3. 在 `CONTRIBUTIONS.md` §二 自己那一行填上"写了什么"
4. 交给 P1 统稿（P1 负责最后一遍数字与格式核对）

## 6.5 工作记录（只记进度，不放正文）

仓库里有一个 **[`submissions/WORKLOG.md`](../submissions/WORKLOG.md)**：**流水账**，只记
"谁在什么时候做了什么"（例如"今天录完了 90 秒 demo 视频"）。

- 报告正文在**金山文档**写，PPT 在**金山 PPT** 做 —— **不要**把正文/PPT 放进仓库
- 每次做完一件事，在 `WORKLOG.md` **末尾追加**一条，不要改别人的记录
- 好处：彼此知道进度、P1 统稿知道哪节还空着、期末个人贡献报告有素材

```bash
git pull
# 在 submissions/WORKLOG.md 末尾追加一段
git add submissions/WORKLOG.md
git commit -m "worklog: 写完了第 1 节初稿"
git push
```

> 除 `submissions/` 外，仓库其它目录（`src/`、`analysis/`、`results/`、`splits/`、`docs/`）一律只读。

## 7. PPT / 演示流程（S1、S2）

1. S1：打开 https://www.kdocs.cn/l/co7EkTOqxwN0 ，15 页已按结果逻辑排好；每页补要点 + 备注里的讲稿与时间
2. S2：按 [`docs/DEMO.md`](DEMO.md) §2–§4 准备；**照 §9 录 90 秒 `demo_fallback.mp4`**（放桌面，断网时兜底）
3. 两人一起彩排，掐表 **≤15:00**；Q&A 5 分钟（卡片见 DEMO.md §6 的 8 个问题）

---

## 8. 提交前（P1 + 组长）

按 [`docs/SUBMISSION.md`](SUBMISSION.md) §七 的 24 项清单逐条打勾。三个硬指标：

- 正文 **2,000–4,000 词**（≤4,400）
- 三件套齐全：**报告 docx + PPT + 源码 zip**，全部在 **2026-11-30 17:00** 前上传 Moodle + Turnitin
- 8 份个人贡献报告（各 300–600 词）
