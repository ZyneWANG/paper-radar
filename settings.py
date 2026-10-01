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
    '研究方向：生成式AI × 交互/游戏化叙事 × 非物质文化遗产现代化传播的交叉领域。'
    '关注生成式AI/大模型/生成式智能体的人机共创、交互式数字叙事/数字故事/游戏化/严肃游戏/'
    '对话式智能体，以及这些技术对非遗与文化遗产的数字化传承、传播与教育，'
    '并关注本真性、人的能动性、文化权利、偏见与文化同质化等伦理议题。')
SCORE_THRESHOLD = int(_val('SCORE_THRESHOLD', '7'))
MAX_PICK = int(_val('MAX_PICK', '12'))

# ---- 邮件 ----
SENDER_EMAIL = _val('SENDER_EMAIL', '')
SENDER_AUTH_CODE = _val('SENDER_AUTH_CODE', '')
RECEIVER_EMAIL = _val('RECEIVER_EMAIL', '')

# ---- 第 6 关：OpenAlex（正式出版论文） ----
OPENALEX_KEY = _val('OPENALEX_KEY', '')
OPENALEX_QUERIES = _list('OPENALEX_QUERIES', [
    # ① 精准档：生成式AI × 交互叙事/游戏 × 非遗
    'generative AI interactive narrative intangible cultural heritage',
    'large language model digital storytelling cultural heritage',
    'generative AI serious game traditional craft heritage',
    # ② 核心档：非遗/遗产 ×（AI 或 游戏化）
    'intangible cultural heritage generative artificial intelligence',
    'cultural heritage gamification game-based learning',
    'digital heritage AI co-creation interactive',
    # ③ 技术雷达档：生成式AI × 交互叙事/游戏
    'generative AI interactive storytelling game',
    'large language model role-playing NPC conversational agent',
    # ④ 伦理档：文化遗产 × AI 伦理
    'cultural heritage AI ethics authenticity human agency',
    'intangible heritage generative AI cultural rights homogenization',
])
OPENALEX_DAYS = int(_val('OPENALEX_DAYS', '365'))
OPENALEX_PER_QUERY = int(_val('OPENALEX_PER_QUERY', '12'))

# ---- 第 6 关：飞书 ----
FEISHU_WEBHOOK = _val('FEISHU_WEBHOOK', '')
FEISHU_SECRET = _val('FEISHU_SECRET', '')

# ---- 第 6 关：渠道开关 ----
ENABLE_EMAIL = _bool('ENABLE_EMAIL', True)
ENABLE_FEISHU = _bool('ENABLE_FEISHU', True)

# ---- 负向关键词：标题/摘要命中即剔除（本地降噪） ----
NEGATIVE_KEYWORDS = _list('NEGATIVE_KEYWORDS', [
    'game theory', 'game-theoretic', 'nash equilibrium', 'gambling', 'betting',
    'lottery', 'gaming disorder', 'narrative medicine', 'narrative therapy',
    'cancer', 'clinical trial', 'craft beer',
])

# ---- 第 6 关：文件位置 ----
SEEN_FILE = 'seen.json'
DOCS_DIR = 'docs'
ARCHIVE_DIR = 'docs/archive'
