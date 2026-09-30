# -*- coding: utf-8 -*-
# 公开模板：把本文件复制为 config.py，再填入你自己的值（config.py 已在 .gitignore 中，不会上传）。

DEEPSEEK_API_KEY = "sk-你的key"

RESEARCH_INTEREST = (
    "你的研究方向，例如：人机交互（HCI），生成式AI与人机协同、AI辅助创意设计、"
    "信息可视化、VR/AR、用户研究。"
)

SCORE_THRESHOLD = 7
MAX_PICK = 12

SENDER_EMAIL = "yourmail@qq.com"
SENDER_AUTH_CODE = "你的SMTP授权码"
RECEIVER_EMAIL = "yourmail@qq.com"


# ============ 第 6 关：OpenAlex（正式出版论文） ============
OPENALEX_KEY = "你的OpenAlex Key（openalex.org/settings/api）"
OPENALEX_QUERIES = [
    "human-AI collaborative design",
    "generative AI creativity support tool",
    "immersive VR AR interaction",
    "human-computer interaction user study",
]
OPENALEX_DAYS = 365
OPENALEX_PER_QUERY = 25


# ============ 第 6 关：飞书推送（可选） ============
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxx"
FEISHU_SECRET = "飞书签名校验密钥"


# ============ 渠道开关 ============
ENABLE_EMAIL = True
ENABLE_FEISHU = True

