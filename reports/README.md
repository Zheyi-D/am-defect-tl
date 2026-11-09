# reports/ —— 报告与演示的**归档**目录（不是协同写作的地方）

> ⚠️ 报告正文在 **Word Online** 里协同编辑，PPT 在 **PowerPoint** 里做。
> 本目录只负责两件事：**存放仓库生成的素材**、**在定稿时存档一份快照**。
> 原因：`docx` / `pptx` 是二进制文件，Git 无法合并两个人的同时编辑 —— 每次改都提交一份只会制造版本地狱。

---

## 目录结构

| 路径 | 放什么 | 谁生成 |
|---|---|---|
| `reports/tables/` | 5 张报告表格（`table1…table5` × `.md` + `.tex`） | `python -m analysis.export_tables` 自动生成，**不要手改** |
| `reports/submission/` | **定稿快照**：最终 `.docx` / `.pptx` / 源码 `.zip`（11/29 放一次即可） | 组长在定稿当天放入 |
| `reports/README.md` | 本文件 | — |

图不在本目录 —— 全部在 **`results/figures/`**，图号与 caption 见 [`results/figures/INDEX.md`](../results/figures/INDEX.md)。

---

## 写报告时怎么取材

| 你需要 | 去哪里拿 |
|---|---|
| 表格（可直接粘进 Word/LaTeX） | `reports/tables/table*.md`（Word 用）或 `*.tex`（LaTeX 用） |
| 图（Figure 1–N） | `results/figures/fig_*.png`，图号与英文 caption 查 `INDEX.md` |
| 所有数字 | **只认** `results/leaderboard.csv` 与 `reports/tables/`，不要自己算 |
| 方法/数据细节 | `README.md`、`docs/DATA.md`、`docs/AUTHOR_CODE.md` |
| 已知限制 | `README.md` §8 |
| 引用信息 | `README.md` §7、`NOTICE.md` |

---

## 定稿归档规范（11/29）

```text
reports/submission/
├── IDAT7215_Topic4_Report_Final.docx      # 报告定稿
├── IDAT7215_Topic4_Slides_Final.pptx      # 口头报告
├── am-defect-tl-src.zip                   # 源码（git archive 生成，见 docs/SUBMISSION.md）
└── README.txt                             # 三件套清单 + 提交时间
```

**只在定稿时提交一次。** 过程中的每一版请留在 Word Online 的版本历史里，不要反复提交 docx。

---

## 三条禁令

1. ❌ 不要手改 `reports/tables/*` —— 它们由 `analysis/export_tables.py` 生成，手改会在下次生成时被覆盖
2. ❌ 不要在 `reports/` 里放中间版 docx（`v2`、`最终版`、`真的最终版`…）
3. ❌ 不要把图复制到 `reports/` —— 一律引用 `results/figures/`，避免两份不一致
