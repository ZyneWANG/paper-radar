# paper-radar · 私人 AI 论文雷达

自动抓取你关注方向的最新论文，用大模型打分筛选并写中文一句话摘要，
定时推送到**邮箱和飞书**，并生成**网页归档**。全程只用 Python 标准库，定时由 GitHub Actions 完成。

- **数据源**：arXiv（预印本、带 PDF）+ OpenAlex（CHI / UIST / CSCW 等正式出版论文，免费 Key）
- **AI 筛选**：DeepSeek 打分（0–10）、写中文摘要，顶会论文质量分适当上浮
- **推送渠道**：HTML 邮件（SMTP）+ 飞书群机器人（interactive 卡片，签名校验）
- **跨周去重**：已推送指纹存 `seen.json`，同一篇不会反复推
- **网页归档**：每期生成静态页，GitHub Pages 在线浏览

## 工作流程（`main.py` 一键串联）

1. `fetch.py`：arXiv 拉取关注分类（默认 `cs.HC`）最近 N 天论文
2. `fetch_openalex.py`：OpenAlex 按搜索词 + 日期窗口拉取正式出版论文
3. `dedup.py`：跨源合并去重、互补字段；按 `seen.json` 过滤掉已推送论文
4. `rank.py`：DeepSeek 打分、筛选、写中文摘要 → `picks.json`
5. `render.py`：生成 HTML 邮件 → `email.html`
6. `send.py` / `notify_feishu.py`：发邮件 / 推飞书
7. `archive_digest.py`：生成 `docs/archive/期次.html` 与 `docs/index.html`
8. 更新 `seen.json`；Actions 结束时自动 commit 去重记录与归档（`[skip ci]`）

## 本地运行

1. 复制 `config.example.py` 为 `config.py`，填入 DeepSeek Key、研究兴趣、邮箱与 SMTP 授权码；
2. （可选）填入 OpenAlex Key、飞书 Webhook 与签名密钥；
3. 运行：`python main.py`。

## 部署到 GitHub（每周自动）

1. 新建仓库并推送本项目；
2. 运行 `python set_secrets.py`，自动把 `config.py` 的值写入 GitHub Secrets（值不回显）；
   涉及的 Secrets：`DEEPSEEK_API_KEY`、`RESEARCH_INTEREST`、`SCORE_THRESHOLD`、`MAX_PICK`、
   `SENDER_EMAIL`、`SENDER_AUTH_CODE`、`RECEIVER_EMAIL`、
   `OPENALEX_KEY`、`OPENALEX_QUERIES`、`OPENALEX_DAYS`、`OPENALEX_PER_QUERY`、
   `FEISHU_WEBHOOK`、`FEISHU_SECRET`、`ENABLE_EMAIL`、`ENABLE_FEISHU`；
3. `.github/workflows/digest.yml` 每周一（北京时间约 09:00）自动运行，也可在 Actions 页手动触发。

## 网页归档（GitHub Pages）

仓库设为 public，在 **Settings → Pages** 选择 `main` 分支的 `/docs` 目录，
即可得到归档首页（示例）：`https://<你的用户名>.github.io/paper-radar/`。

## 自定义

- 修改 `fetch.py` 顶部的 `CATEGORIES`、`KEYWORDS`、`DAYS`；
- 修改 `config.py` 的 `OPENALEX_QUERIES`（正式论文搜索词）、研究兴趣与阈值。
