# -*- coding: utf-8 -*-
"""
去重工具：
- fp()        生成论文指纹（DOI / arXiv id / 归一化标题）
- merge_dedup 多源候选合并、跨源去重并互补字段
- seen 相关   跨周去重：记录已推送指纹，持久化到 seen.json
"""
import os
import re
import json
from datetime import datetime, timezone

import settings


def norm_title(t):
    t = (t or '').lower()
    return re.sub(r'[^a-z0-9一-鿿]+', '', t)


def fp(p):
    doi = (p.get('doi') or '').lower().replace('https://doi.org', '').strip('/')
    if doi:
        return 'doi:' + doi
    au = p.get('abs_url', '') or ''
    if 'arxiv.org/abs/' in au:
        return 'arxiv:' + au.split('/abs/')[-1].split('v')[0]
    if p.get('id'):
        return p.get('source', 'x').lower() + ':' + str(p['id'])
    return 't:' + norm_title(p['title'])


def merge_dedup(*lists):
    out = {}
    for papers in lists:
        for p in papers:
            k = fp(p)
            if k in out:
                a = out[k]
                for fld in ('pdf_url', 'venue', 'doi', 'summary', 'abs_url'):
                    if not a.get(fld) and p.get(fld):
                        a[fld] = p[fld]
            else:
                out[k] = p
    return list(out.values())


def filter_negative(papers):
    """剔除标题/摘要命中负向关键词的候选（本地降噪）。"""
    negs = [w.lower() for w in settings.NEGATIVE_KEYWORDS if w]
    if not negs:
        return papers
    kept, dropped = [], 0
    for p in papers:
        blob = ((p.get('title') or '') + ' ' + (p.get('summary') or '')).lower()
        if any(n in blob for n in negs):
            dropped += 1
            continue
        kept.append(p)
    if dropped:
        print('负向词过滤：剔除 %d 篇，剩 %d 篇。' % (dropped, len(kept)))
    return kept


# ---------- 跨周去重 ----------
def load_seen():
    if os.path.exists(settings.SEEN_FILE):
        try:
            return json.load(open(settings.SEEN_FILE, encoding='utf-8'))
        except Exception:
            return {}
    return {}


def filter_unseen(papers, seen):
    return [p for p in papers if fp(p) not in seen]


def update_seen(papers, seen):
    today = datetime.now(timezone.utc).date().isoformat()
    for p in papers:
        seen[fp(p)] = today
    if len(seen) > 1000:  # 只保留最近 1000 条指纹
        seen = dict(sorted(seen.items(), key=lambda kv: kv[1], reverse=True)[:1000])
    return seen


def save_seen(seen):
    with open(settings.SEEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)
