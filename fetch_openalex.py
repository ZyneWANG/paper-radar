# -*- coding: utf-8 -*-
"""
第 6 关 · 从 OpenAlex 抓正式出版论文（CHI / UIST / CSCW 等）
- 免费 API Key（openalex.org/settings/api），作为 api_key 参数传入；
- 按搜索词 + 日期窗口拉取，重建倒排摘要，映射成统一 paper 字段；
- 自带 429 退避重试；全程只用标准库。
"""
import json
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta, timezone

import settings

OPENALEX = 'https://api.openalex.org/works'


def _get_json(url, tries=6):
    for n in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'paper-radar/1.0'})
            with urllib.request.urlopen(req, timeout=40) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            wait = 5 * (n + 1)
            if e.code == 429:
                try:
                    body = json.loads(e.read().decode('utf-8'))
                    wait = int(body.get('retryAfter', wait)) + 2
                except Exception:
                    ra = e.headers.get('Retry-After')
                    if ra and ra.isdigit():
                        wait = int(ra) + 2
            elif e.code in (403, 404):
                return None
            time.sleep(wait)
        except Exception:
            time.sleep(4 * (n + 1))
    return None


def _rebuild_abstract(inv):
    if not inv:
        return ''
    positions = {}
    length = 0
    for word, poses in inv.items():
        for i in poses:
            positions[i] = word
            length = max(length, i + 1)
    return ' '.join(positions.get(i, '') for i in range(length)).strip()


def fetch_one_query(query):
    start = (datetime.now(timezone.utc) - timedelta(days=settings.OPENALEX_DAYS)).date().isoformat()
    params = {
        'search': query,
        'filter': 'from_publication_date:%s,has_abstract:true' % start,
        'sort': 'publication_date:desc',
        'per-page': settings.OPENALEX_PER_QUERY,
        'select': 'display_name,publication_date,doi,authorships,abstract_inverted_index,'
                  'primary_location,best_oa_location,open_access',
        'mailto': settings.SENDER_EMAIL or 'example@example.com',
    }
    if settings.OPENALEX_KEY:
        params['api_key'] = settings.OPENALEX_KEY
    data = _get_json(OPENALEX + '?' + urllib.parse.urlencode(params))
    if not data:
        return []
    papers = []
    for w in data.get('results', []):
        src = (w.get('primary_location') or {}).get('source') or {}
        venue = src.get('display_name', '')
        best = w.get('best_oa_location') or {}
        doi = w.get('doi') or ''
        landing = (w.get('primary_location') or {}).get('landing_page_url') or ''
        pdf = best.get('pdf_url') or (w.get('open_access') or {}).get('oa_url') or ''
        abs_url = doi or landing
        papers.append({
            'title': w.get('display_name', ''),
            'summary': _rebuild_abstract(w.get('abstract_inverted_index')),
            'authors': [a.get('author', {}).get('display_name', '')
                        for a in w.get('authorships', [])],
            'abs_url': abs_url,
            'pdf_url': pdf,
            'published': w.get('publication_date', ''),
            'source': 'OpenAlex',
            'venue': venue,
            'doi': doi,
        })
    return papers


def main():
    allp = []
    for q in settings.OPENALEX_QUERIES:
        got = fetch_one_query(q)
        print('OpenAlex 查询「%s」-> %d 篇' % (q, len(got)))
        allp.extend(got)
        time.sleep(1)
    with open('openalex.json', 'w', encoding='utf-8') as f:
        json.dump(allp, f, ensure_ascii=False, indent=2)
    print('共取 %d 篇（未跨源去重），已存 openalex.json' % len(allp))


if __name__ == '__main__':
    main()
