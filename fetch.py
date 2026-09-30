# -*- coding: utf-8 -*-
"""
第 1 关 · 抓论文
从 arXiv（免费、无需 Key、带 PDF）拉取你关注分类下最近 N 天的论文，
解析出 标题 / 作者 / 摘要 / 原文链接 / PDF 链接，存成 papers.json。
全程只用 Python 标准库，不用 pip 安装任何东西。
"""
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

# ============ 你可以改的配置 ============
CATEGORIES = ['cs.HC']          # 人机交互；想加可写 ['cs.HC','cs.GR','cs.CV']
KEYWORDS = []                   # 留 [] = 分类下全要，候选全交给 AI 筛选；
                                # 想只看某些主题可填 ['creativity','human-AI','visualization','VR']
MAX_RESULTS = 40                # 每次最多拉多少篇（候选池）
DAYS = 14                       # 只要最近多少天提交的
# =======================================

ARXIV_API = 'http://export.arxiv.org/api/query'


def fetch_raw():
    cat_query = ' OR '.join('cat:' + c for c in CATEGORIES)
    qs = urllib.parse.urlencode({
        'search_query': cat_query,
        'start': 0,
        'max_results': MAX_RESULTS,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending',
    })
    req = urllib.request.Request(
        ARXIV_API + '?' + qs,
        headers={'User-Agent': 'paper-radar/1.0 (contact: example@example.com)'},
    )
    with urllib.request.urlopen(req, timeout=40) as resp:
        return resp.read()


def parse(raw):
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    root = ET.fromstring(raw)
    cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS)
    papers = []
    for e in root.findall('a:entry', ns):
        published = datetime.fromisoformat(
            e.find('a:published', ns).text.replace('Z', '+00:00'))
        if published < cutoff:
            continue
        title = ' '.join(e.find('a:title', ns).text.split())
        summary = ' '.join(e.find('a:summary', ns).text.split())
        abs_url = e.find('a:id', ns).text.strip()
        pdf_url = ''
        for link in e.findall('a:link', ns):
            if link.get('title') == 'pdf':
                pdf_url = link.get('href')
        authors = [a.find('a:name', ns).text for a in e.findall('a:author', ns)]
        if KEYWORDS:
            blob = (title + ' ' + summary).lower()
            if not any(k.lower() in blob for k in KEYWORDS):
                continue
        papers.append({
            'title': title,
            'summary': summary,
            'authors': authors,
            'abs_url': abs_url,
            'pdf_url': pdf_url,
            'published': published.date().isoformat(),
            'source': 'arXiv',
        })
    return papers


def main():
    raw = fetch_raw()
    papers = parse(raw)
    with open('papers.json', 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    print('抓到 %d 篇（最近 %d 天），已存 papers.json' % (len(papers), DAYS))
    for i, p in enumerate(papers[:10], 1):
        print('\n[%d] %s  (%s)' % (i, p['title'], p['published']))
        print('    ' + p['summary'][:150] + ' ...')
        print('    PDF: ' + p['pdf_url'])
    if len(papers) > 10:
        print('\n（只预览前 10 篇，全部在 papers.json 里）')


if __name__ == '__main__':
    main()
