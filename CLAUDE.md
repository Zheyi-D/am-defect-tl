# CLAUDE.md

本仓库的 agent 说明统一写在 **[AGENTS.md](AGENTS.md)**（含仓库事实、产物契约、不变量、已知坑）。

**写报告 / 做 PPT / 录演示的同学（及其 AI agent）：先读 [docs/START-HERE.md](docs/START-HERE.md)。**

三条最容易犯的错：

1. 自己估算或编造数字 —— 一律以 `results/leaderboard.csv` / `reports/tables/` 为准
2. 把泄漏对照实验写成"我们证明了数据泄漏"（实际结论是**阴性**）
3. 把 D2 说成独立数据集（D2 是 D1 的数据增强版）

唯一允许非维护者写入的地方：`submissions/WORKLOG.md`（只在末尾追加工作记录，不放正文）。
