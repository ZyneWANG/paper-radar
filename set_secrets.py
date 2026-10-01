# -*- coding: utf-8 -*-
"""一次性脚本：把本地 config.py 的值写入 GitHub Secrets（值不回显、不进命令行）。
空值自动跳过，避免覆盖已设置好的 Secret。"""
import json
import subprocess
import config

GH = r"C:\Program Files\GitHub CLI\gh.exe"
REPO = "ZyneWANG/paper-radar"

secrets = {
    # 核心
    "DEEPSEEK_API_KEY": config.DEEPSEEK_API_KEY,
    "RESEARCH_INTEREST": config.RESEARCH_INTEREST,
    "SCORE_THRESHOLD": str(config.SCORE_THRESHOLD),
    "MAX_PICK": str(config.MAX_PICK),
    # 邮件
    "SENDER_EMAIL": config.SENDER_EMAIL,
    "SENDER_AUTH_CODE": config.SENDER_AUTH_CODE,
    "RECEIVER_EMAIL": config.RECEIVER_EMAIL,
    # 第 6 关：OpenAlex
    "OPENALEX_KEY": config.OPENALEX_KEY,
    "OPENALEX_QUERIES": json.dumps(config.OPENALEX_QUERIES, ensure_ascii=False),
    "OPENALEX_DAYS": str(config.OPENALEX_DAYS),
    "OPENALEX_PER_QUERY": str(config.OPENALEX_PER_QUERY),
    # 第 6 关：飞书
    "FEISHU_WEBHOOK": config.FEISHU_WEBHOOK,
    "FEISHU_SECRET": config.FEISHU_SECRET,
    # 渠道开关
    "ENABLE_EMAIL": str(config.ENABLE_EMAIL),
    "ENABLE_FEISHU": str(config.ENABLE_FEISHU),
    # 负向关键词
    "NEGATIVE_KEYWORDS": json.dumps(config.NEGATIVE_KEYWORDS, ensure_ascii=False),
}

for name, value in secrets.items():
    if value == '' or value is None:
        print("%-18s -> (空，跳过)" % name)
        continue
    r = subprocess.run([GH, "secret", "set", name, "--repo", REPO],
                       input=value, text=True, capture_output=True)
    print("%-18s -> %s" % (name, "OK" if r.returncode == 0 else "FAIL " + r.stderr))
