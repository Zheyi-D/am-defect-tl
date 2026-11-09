# submissions/ —— 6 位同学的提交区（只写自己那一格）

> **一句话规则：你只能写 `submissions/<你的代号>/` 里的文件，别的地方一律不许动。**

已完成的代码、实验、图表、表格都在仓库其他目录，**全部是只读的**；
本目录是唯一给你写东西的地方（在线文档另外算，见 §4）。

---

## 1. 目录分配（一人一格，互不重叠）

| 代号 | 你的目录 | 你负责的内容 |
|---|---|---|
| **P1** | `submissions/P1/` | Abstract、§4 Conclusion、统稿记录 |
| **P2** | `submissions/P2/` | §1 Introduction、References |
| **P3** | `submissions/P3/` | §2 Project Description（含 Algorithm 1） |
| **P4** | `submissions/P4/` | §3 Results and Discussion、图表排版说明 |
| **S1** | `submissions/S1/` | 15 页 PPT 大纲、讲稿、彩排计时 |
| **S2** | `submissions/S2/` | demo 计划、录屏说明（**视频不进仓库**，只放链接） |

---

## 2. 绝对不能碰的地方（改了会造成结果不可比 / 直接扣分）

| 路径 | 为什么 |
|---|---|
| `src/`、`analysis/`、`tools/`、`tests/` | 代码，改了就破坏 66 个实验的可比性 |
| `results/`（含 `leaderboard.csv`、`runs/`、`figures/`） | 实验结果与图表，**数字唯一来源**，手改即造假 |
| `splits/` | 数据划分已冻结（改了必须重跑全部 66 个 run） |
| `docs/`、`README.md`、`AGENTS.md` | 项目文档，由维护者维护（`docs/START-HERE.md` 可读不可改） |
| 其他人的 `submissions/<代号>/` | 别人的格子 |

> 想改上面任何一项 → 在群里问，由 Kenneth 来改，不要自己动。

---

## 3. 上传方式（每人只推自己的分支）

```bash
# 1) 克隆（只做一次）
git clone https://github.com/Zheyi-D/am-defect-tl.git
cd am-defect-tl

# 2) 只把文件放进自己的目录
#    例如 P2：
#    submissions/P2/P2_introduction.md
#    submissions/P2/P2_references.md

# 3) 提交并推到你自己的分支（分支名 = submissions/<你的代号>）
git add submissions/P2
git commit -m "P2: section 1 draft"
git push origin HEAD:submissions/P2
```

**然后再推一次就自动更新同一个分支**，不需要新建分支。
Kenneth 会定期把这些分支合并进 `main`（你不需要、也不应该去碰 `main`）。

> 用 AI 的话，直接把本节发给它：「只允许修改 `submissions/<我的代号>/`，其它路径一律不碰，
> 提交到 `submissions/<我的代号>` 分支，不要 push main。」

---

## 4. 和在线文档的关系

| 你在哪写 | 用来做什么 |
|---|---|
| **在线文档**（金山文档，链接见 `docs/START-HERE.md`） | 多人协同写**正文**，最终交付从这里导出 docx |
| **`submissions/<代号>/`（本目录）** | 存一份 **Markdown 备份**：便于 P1 合稿、留版本记录、给 AI 复查 |

推荐流程：先在在线文档写 → 定稿那一节后，把你写的内容另存为 Markdown 放进自己的目录（文件名见各目录 README）。

---

## 5. 文件规范

- 格式：**Markdown**，纯文字；**不要把图复制进仓库**，用图号引用（如 `Figure 7`，清单见 `results/figures/CATALOG.md`）
- 表格：从 `reports/tables/table*.md` 复制，**不要手打数字**
- 文件名：`<代号>_<内容>.md`（每个目录的 README 里列了允许的文件名）
- 每个目录放一个 `status.md`，写：状态 / 字数 / 最后更新日期

---

## 6. 提交前自检（30 秒）

- [ ] `git status` 里只有 `submissions/<我的代号>/` 下的文件
- [ ] 没有动 `src/`、`analysis/`、`results/`、`splits/`、`docs/`
- [ ] 推送目标是 `submissions/<我的代号>` 分支，不是 `main`
- [ ] 文档里每个数字都能在 `results/leaderboard.csv` 或 `reports/tables/` 里找到
