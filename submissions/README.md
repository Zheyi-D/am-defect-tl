# submissions/ —— 工作记录区（就一个文件）

> **唯一可以写的东西：[`WORKLOG.md`](WORKLOG.md)。**
> 这里只记"谁在什么时候做了什么"，**不放报告或 PPT 的内容**。

---

## 1. 这里放什么 / 不放什么

| ✅ 放 | ❌ 不放 |
|---|---|
| "今天写完了 1.1–1.4 初稿" | 报告正文（在金山文档里写） |
| "录完了 90 秒 demo 视频，存桌面" | PPT 内容（在金山 PPT 里做） |
| "PPT 前 6 页做完了，卡在第 7 页的图" | 代码、图表、表格、数字 |
| "等 Kenneth 确认 Fig. 1 放哪" | 任何要提交的东西 |

一句话：**这里只是流水账 / 备忘录**，方便彼此知道进度，也给个人贡献报告留素材。

---

## 2. 怎么用（3 步）

1. 打开 `WORKLOG.md`，**拉到最底下**
2. 在末尾**追加**一段（照文件里给的格式写）
3. 保存 → 推送（命令见 §4）

> 只追加、不删改别人的内容。一行也行，几行也行。

---

## 3. 绝对不能碰的地方

| 路径 | 为什么 |
|---|---|
| `src/`、`analysis/`、`tools/`、`tests/` | 代码，改了会破坏 66 个实验的可比性 |
| `results/`（`leaderboard.csv`、`runs/`、`figures/`） | 实验结果与图，**数字唯一来源**，手改即造假 |
| `splits/` | 数据划分已冻结 |
| `docs/`、`reports/`、`README.md`、`AGENTS.md` | 项目文档，由维护者维护 |
| `submissions/README.md` | 本文件（一般不用改） |

---

## 4. 怎么推送

```bash
# 第一次
git clone https://github.com/Zheyi-D/am-defect-tl.git
cd am-defect-tl

# 以后每次
git pull
#   在 submissions/WORKLOG.md 末尾追加一段
git add submissions/WORKLOG.md
git commit -m "worklog: 写完了第 1 节初稿"
git push
```

> 报冲突就先 `git pull` 再改；解决不了就把你那段发群里，让 Kenneth 帮你合 ——
> **不要为了推上去删别人的记录**。

---

## 5. 用 AI 的话，把这段发给它

```text
在 D:\...\am-defect-tl 仓库里，帮我在 submissions/WORKLOG.md 的末尾追加一条工作记录。

规则：
- 只追加，不要修改或删除文件里已有的任何内容
- 不要改仓库其它任何文件（src/ analysis/ results/ splits/ docs/ reports/ 等）
- 按文件里给的格式写：## 日期 · 名字，下面列 做了什么 / 产出在哪 / 卡在哪
- 写完后 git add submissions/WORKLOG.md && git commit && git push
```

---

## 6. 和三个地方的分工

| 地方 | 用途 |
|---|---|
| 金山文档（报告） | 写正文，最后导出 docx 提交 |
| 金山 PPT | 做幻灯片 + 录屏说明 |
| **`submissions/WORKLOG.md`（这里）** | **只记进度：做了啥、卡在哪** |
| `CONTRIBUTIONS.md` | 期末个人贡献报告的正式素材（从工作记录里提炼） |
