# -*- coding: utf-8 -*-
"""
一键入口：抓论文 → AI 筛选打分 → 排邮件 → 发送。
GitHub Actions 定时运行的就是这个文件；本地也可以直接 python main.py。
"""
import fetch
import rank
import render
import send


def main():
    fetch.main()
    rank.main()
    render.main()
    send.main()


if __name__ == '__main__':
    main()
