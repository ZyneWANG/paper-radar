# -*- coding: utf-8 -*-
# 公开模板：把本文件复制为 config.py，再填入你自己的值（config.py 已在 .gitignore 中，不会上传）。

DEEPSEEK_API_KEY = "sk-你的key"

RESEARCH_INTEREST = (
    "你的研究方向，例如：生成式AI × 交互/游戏化叙事 × 非物质文化遗产现代化传播的交叉领域，"
    "关注大模型人机共创、交互叙事/游戏化/对话式智能体、非遗数字传承与相关伦理。"
)

SCORE_THRESHOLD = 7
MAX_PICK = 12

SENDER_EMAIL = "yourmail@qq.com"
SENDER_AUTH_CODE = "你的SMTP授权码"
RECEIVER_EMAIL = "yourmail@qq.com"


# ============ 第 6 关：OpenAlex（正式出版论文） ============
OPENALEX_KEY = "你的OpenAlex Key（openalex.org/settings/api）"
# 把「4 档布尔检索」翻译成多词 AND 查询（OpenAlex 不支持括号/OR/通配符，同义词多列几条）
OPENALEX_QUERIES = [
    # ① 精准档：生成式AI × 交互叙事/游戏 × 非遗
    "generative AI interactive narrative intangible cultural heritage",
    "large language model digital storytelling cultural heritage",
    "generative AI serious game traditional craft heritage",
    # ② 核心档：非遗/遗产 ×（AI 或 游戏化）
    "intangible cultural heritage generative artificial intelligence",
    "cultural heritage gamification game-based learning",
    "digital heritage AI co-creation interactive",
    # ③ 技术雷达档：生成式AI × 交互叙事/游戏
    "generative AI interactive storytelling game",
    "large language model role-playing NPC conversational agent",
    # ④ 伦理档：文化遗产 × AI 伦理
    "cultural heritage AI ethics authenticity human agency",
    "intangible heritage generative AI cultural rights homogenization",
]
OPENALEX_DAYS = 365
OPENALEX_PER_QUERY = 12


# ============ 第 6 关：飞书推送（可选） ============
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxx"
FEISHU_SECRET = "飞书签名校验密钥"


# ============ 渠道开关 ============
ENABLE_EMAIL = True
ENABLE_FEISHU = True


# ============ 负向关键词（标题/摘要命中即剔除，降噪） ============
NEGATIVE_KEYWORDS = [
    "game theory", "game-theoretic", "nash equilibrium", "gambling", "betting",
    "lottery", "gaming disorder", "narrative medicine", "narrative therapy",
    "cancer", "clinical trial", "craft beer",
]

