# paper-radar · 私人 AI 论文雷达

自动抓取你关注方向的最新论文，用大模型打分筛选并写中文一句话摘要，排版成 HTML 邮件，
定时发到你的邮箱。数据来自 arXiv（免费、带 PDF），筛选使用 DeepSeek，定时由 GitHub Actions 完成。
全程只用 Python 标准库。

## 工作流程

1. `fetch.py`：从 arXiv 拉取关注分类（默认 `cs.HC`）最近 N 天的论文 → `papers.json`
2. `rank.py`：DeepSeek 打分（0–10）、筛选、写中文摘要 → `picks.json`
3. `render.py`：生成 HTML 邮件 → `email.html`
4. `send.py`：通过 SMTP 发送到你的邮箱
5. `main.py`：一键串联以上四步

## 本地运行

1. 复制 `config.example.py` 为 `config.py`，填入你的 DeepSeek Key、研究兴趣、邮箱与 SMTP 授权码；
2. 运行：`python main.py`（也可逐个运行四个脚本）。

## 部署到 GitHub（每周自动）

1. 新建一个 GitHub 仓库并推送本项目；
2. 在仓库 **Settings → Secrets and variables → Actions** 添加以下 Secrets：
   `DEEPSEEK_API_KEY`、`RESEARCH_INTEREST`、`SCORE_THRESHOLD`、`MAX_PICK`、
   `SENDER_EMAIL`、`SENDER_AUTH_CODE`、`RECEIVER_EMAIL`；
3. `.github/workflows/digest.yml` 会在每周一（北京时间约 09:00）自动运行；
   也可在 **Actions** 页手动触发（Run workflow）。

## 自定义

- 修改 `fetch.py` 顶部的 `CATEGORIES`（如加 `cs.GR`、`cs.CV`）、`KEYWORDS`、`DAYS`；
- 修改 `config.py` 的研究兴趣与阈值即可调整筛选口味。
