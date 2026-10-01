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
CATEGORIES = ['cs.HC', 'cs.CL', 'cs.AI', 'cs.IR']
KEYWORDS = []                   # 留 []；下面的布尔查询已经做了主题过滤
MAX_RESULTS = 50                # 每次最多拉多少篇（候选池）
DAYS = 21                       # 只要最近多少天提交的
# =======================================

ARXIV_API = 'http://export.arxiv.org/api/query'

# 研究方向三簇：A=生成式AI，B=交互/游戏化叙事，C=非遗/文化遗产
_A = ('all:"generative AI" OR all:"large language model" OR all:LLM OR '
      'all:ChatGPT OR all:GenAI OR all:"AI agent" OR all:"generative agent"')
_B = ('all:"interactive narrative" OR all:storytelling OR all:gamification OR '
      'all:"serious game" OR all:"role-playing" OR all:NPC OR all:"conversational agent"')
_C = ('all:"intangible cultural heritage" OR all:"cultural heritage" OR all:"digital heritage" '
      'OR all:museum OR all:"traditional craft" OR all:handicraft')
# arXiv 端先排除一部分高频噪音（其余负向词在本地过滤兜底）
_NEG = ('all:"game theory" OR all:gambling OR all:nash OR all:lottery OR '
        'all:cancer OR all:"narrative medicine" OR all:betting')


def fetch_raw():
    cat_query = ' OR '.join('cat:' + c for c in CATEGORIES)
    # A 且（B 或 C），再排除负向
    full = '(%s) AND ((%s) AND ((%s) OR (%s))) AND NOT (%s)' % (
        cat_query, _A, _B, _C, _NEG)
    qs = urllib.parse.urlencode({
        'search_query': full,
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
