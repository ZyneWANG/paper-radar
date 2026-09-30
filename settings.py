# -*- coding: utf-8 -*-
"""
统一配置入口（这个文件会被上传到 GitHub）。
- 本地运行：从私密的 config.py 读取（已 gitignore，不会上传）；
- GitHub Actions：从环境变量读取，环境变量由 GitHub Secrets 注入。
"""
import os
import json

try:
    import config  # 本地私密文件，GitHub 上不存在
except Exception:
    config = None


def _val(name, default=''):
    if name in os.environ:
        return os.environ[name]
    if config is not None and hasattr(config, name):
        return getattr(config, name)
    return default


def _bool(name, default=True):
    raw = str(_val(name, 'True' if default else 'False')).strip().lower()
    return raw not in ('false', '0', 'no', 'off')


def _list(name, default):
    raw = _val(name, '')
    if isinstance(raw, list):
        return raw
    if raw:
        try:
            v = json.loads(raw)
            if isinstance(v, list):
                return [str(x) for x in v]
        except Exception:
            return [x.strip() for x in raw.split('||') if x.strip()]
    return default


# ---- 核心：DeepSeek 与研究兴趣 ----
DEEPSEEK_API_KEY = _val('DEEPSEEK_API_KEY', '')
RESEARCH_INTEREST = _val(
    'RESEARCH_INTEREST',
    '人机交互（HCI），尤其关注生成式AI与人机协同、AI辅助创意与设计工具、'
    '信息可视化、VR/AR/混合现实、交互界面与用户研究、创造力支持工具。')
SCORE_THRESHOLD = int(_val('SCORE_THRESHOLD', '7'))
MAX_PICK = int(_val('MAX_PICK', '12'))

# ---- 邮件 ----
SENDER_EMAIL = _val('SENDER_EMAIL', '')
SENDER_AUTH_CODE = _val('SENDER_AUTH_CODE', '')
RECEIVER_EMAIL = _val('RECEIVER_EMAIL', '')

# ---- 第 6 关：OpenAlex（正式出版论文） ----
OPENALEX_KEY = _val('OPENALEX_KEY', '')
OPENALEX_QUERIES = _list('OPENALEX_QUERIES', [
    'human-AI collaborative design',
    'generative AI creativity support tool',
    'immersive VR AR interaction',
    'human-computer interaction user study',
])
OPENALEX_DAYS = int(_val('OPENALEX_DAYS', '365'))
OPENALEX_PER_QUERY = int(_val('OPENALEX_PER_QUERY', '25'))

# ---- 第 6 关：飞书 ----
FEISHU_WEBHOOK = _val('FEISHU_WEBHOOK', '')
FEISHU_SECRET = _val('FEISHU_SECRET', '')

# ---- 第 6 关：渠道开关 ----
ENABLE_EMAIL = _bool('ENABLE_EMAIL', True)
ENABLE_FEISHU = _bool('ENABLE_FEISHU', True)

# ---- 第 6 关：文件位置 ----
SEEN_FILE = 'seen.json'
DOCS_DIR = 'docs'
ARCHIVE_DIR = 'docs/archive'
