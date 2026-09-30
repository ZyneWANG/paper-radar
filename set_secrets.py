# -*- coding: utf-8 -*-
"""一次性脚本：把本地 config.py 的值写入 GitHub Secrets（值不回显、不进命令行）。"""
import subprocess
import config

GH = r"C:\Program Files\GitHub CLI\gh.exe"
REPO = "ZyneWANG/paper-radar"

secrets = {
    "DEEPSEEK_API_KEY": config.DEEPSEEK_API_KEY,
    "RESEARCH_INTEREST": config.RESEARCH_INTEREST,
    "SCORE_THRESHOLD": str(config.SCORE_THRESHOLD),
    "MAX_PICK": str(config.MAX_PICK),
    "SENDER_EMAIL": config.SENDER_EMAIL,
    "SENDER_AUTH_CODE": config.SENDER_AUTH_CODE,
    "RECEIVER_EMAIL": config.RECEIVER_EMAIL,
}

for name, value in secrets.items():
    r = subprocess.run([GH, "secret", "set", name, "--repo", REPO],
                       input=value, text=True, capture_output=True)
    print("%-18s -> %s" % (name, "OK" if r.returncode == 0 else "FAIL " + r.stderr))
