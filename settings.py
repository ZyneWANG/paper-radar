# -*- coding: utf-8 -*-
"""
统一配置入口（这个文件会被上传到 GitHub）。
- 本地运行：从私密的 config.py 读取（已 gitignore，不会上传）；
- GitHub Actions：从环境变量读取，环境变量由 GitHub Secrets 注入。
"""
import os

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


DEEPSEEK_API_KEY = _val('DEEPSEEK_API_KEY', '')
RESEARCH_INTEREST = _val(
    'RESEARCH_INTEREST',
    '人机交互（HCI），尤其关注生成式AI与人机协同、AI辅助创意与设计工具、'
    '信息可视化、VR/AR/混合现实、交互界面与用户研究、创造力支持工具。')
SCORE_THRESHOLD = int(_val('SCORE_THRESHOLD', '7'))
MAX_PICK = int(_val('MAX_PICK', '12'))

SENDER_EMAIL = _val('SENDER_EMAIL', '')
SENDER_AUTH_CODE = _val('SENDER_AUTH_CODE', '')
RECEIVER_EMAIL = _val('RECEIVER_EMAIL', '')
