# P4 的提交区

| 项 | 内容 |
|---|---|
| 负责 | §3 Results and Discussion（3.1–3.6）+ 全部图表排版 |
| 目标字数 | 1,400 词（3.1 350 / 3.2 250 / 3.3 300 / 3.4 250 / 3.5 150 / 3.6 100） |
| 参考素材 | `results/leaderboard.csv`（66 行数字）、`reports/tables/table2_d1_results.md` / `table3_d2_results.md` / `table4_delta.md` / `table5_efficiency.md` / `table6_leakage.md`、`results/figures/CATALOG.md`（Fig. 1–10 图号与 caption）、`results/leakage.csv`、`results/efficiency.csv` |
| 完成标准 | 1,400 词 + 六小节齐全 + 图表编号与 CATALOG 完全一致 |

## 只允许在这个目录里建这些文件

- `P4_results.md`
- `P4_figure_table_placement.md`
- `status.md`（必填：状态 / 字数 / 最后更新）

**不要改这个目录以外的任何东西。** 全局规则见 [`../README.md`](../README.md)。

## 提交方式

```bash
git add submissions/P4
git commit -m "P4: draft"
git push origin HEAD:submissions/P4
```

## 注意事项

必须写进三条：① EfficientNet 家族在论文里 F1=0（塌成多数类），不是我们更强；② 泄漏实验是**阴性结论**（|Δ|≤1.5%，多数为负）；③ D1 测试集仅 54 张，0.02 的差距无统计意义。官方还要求讨论“调参如何影响结果”。
