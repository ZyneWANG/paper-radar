# -*- coding: utf-8 -*-
"""
一键入口（GitHub Actions 定时运行此文件，本地也可 python main.py）：
  抓 arXiv + 抓 OpenAlex → 跨源合并去重 → 跨周去重 → DeepSeek 打分精选
  → 排 HTML → 发邮件 / 推飞书 → 网页归档 → 更新去重记录。
"""
import os
import json

import settings
import dedup
import fetch
import fetch_openalex
import rank
import render
import send
import notify_feishu
import archive_digest


def gather():
    # 1) arXiv（失败不致命）
    arxiv = []
    try:
        fetch.main()
        with open('papers.json', encoding='utf-8') as f:
            arxiv = json.load(f)
    except Exception as e:
        print('arXiv 抓取失败（继续其它源）：', e)

    # 2) OpenAlex（需 Key；失败不致命）
    oa = []
    if settings.OPENALEX_KEY:
        try:
            fetch_openalex.main()
            with open('openalex.json', encoding='utf-8') as f:
                oa = json.load(f)
        except Exception as e:
            print('OpenAlex 抓取失败（继续其它源）：', e)
    else:
        print('未配置 OpenAlex Key，跳过正式出版论文源。')

    # 3) 跨源合并去重
    merged = dedup.merge_dedup(arxiv, oa)

    # 4) 跨周去重（只保留没推过的）
    seen = dedup.load_seen()
    fresh = dedup.filter_unseen(merged, seen)
    with open('papers.json', 'w', encoding='utf-8') as f:
        json.dump(fresh, f, ensure_ascii=False, indent=2)
    print('合并候选 %d 篇，其中已推过 %d 篇，本期新候选 %d 篇。'
          % (len(merged), len(merged) - len(fresh), len(fresh)))
    return fresh


def main():
    fresh = gather()
    if not fresh:
        print('本期没有新论文，结束。')
        return

    rank.main()  # 读 papers.json，产出 picks.json
    with open('picks.json', encoding='utf-8') as f:
        picks = json.load(f)
    if not picks:
        print('AI 本期没有筛出值得推送的论文，结束。')
        return

    render.main()
    if settings.ENABLE_EMAIL:
        send.main()
    if settings.ENABLE_FEISHU and settings.FEISHU_WEBHOOK:
        notify_feishu.main()

    archive_digest.main()

    seen = dedup.update_seen(picks, dedup.load_seen())
    dedup.save_seen(seen)
    print('全流程完成，本期推送 %d 篇，已更新去重记录与归档。' % len(picks))


if __name__ == '__main__':
    main()
