# -*- coding: utf-8 -*-
"""
第 6 关 · 网页归档
- 每期生成 docs/archive/YYYY-MM-DD.html（复用 render 的论文卡片）；
- 维护 docs/archive/meta.json，并生成 docs/index.html 归档首页；
- 配合 GitHub Pages（仓库 public，Pages 指向 main/docs）即可在线浏览。
字符串用占位符替换，不用 % 格式化，避免与卡片里的百分号冲突。
"""
import os
import glob
import json
from datetime import date

import settings
import render

META = os.path.join(settings.ARCHIVE_DIR, 'meta.json')

ISSUE_TPL = '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:30px;background:#eef1f5;">
<table width="860" align="center" cellpadding="0" cellspacing="0"
       style="max-width:860px;background:#ffffff;border-radius:14px;overflow:hidden;">
  <tr><td style="background:#14345c;padding:22px 26px;">
    <div style="font:bold 21px 'Microsoft YaHei',Arial;color:#fff;">论文雷达 · HCI 周报归档</div>
    <div style="font:13px Arial;color:#cdd9ec;padding-top:8px;">
      __DATE__ · 精选 __N__ 篇 · <a style="color:#cdd9ec" href="../index.html">&#8592; 返回归档首页</a></div>
  </td></tr>
  <tr><td style="height:16px;"></td></tr>
  __ROWS__
  <tr><td style="padding:8px 26px 24px;font:11px/1.7 Arial;color:#9aa3b2;">
    paper-radar 自动归档 · 数据 arXiv + OpenAlex，DeepSeek 打分并撰写中文摘要，分数 &ge; __TH__ 入选。
  </td></tr>
</table></body></html>'''

INDEX_TPL = '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:34px;background:#eef1f5;">
<table width="720" align="center" cellpadding="0" cellspacing="0"
       style="max-width:720px;background:#ffffff;border-radius:14px;overflow:hidden;">
  <tr><td style="background:#14345c;padding:28px 26px;">
    <div style="font:bold 24px 'Microsoft YaHei',Arial;color:#fff;">论文雷达 · 归档首页</div>
    <div style="font:13px Arial;color:#cdd9ec;padding-top:10px;line-height:1.6;">
      每周自动归档 HCI 精选论文 · 数据源 arXiv + OpenAlex</div>
  </td></tr>
  __LIST__
  <tr><td style="padding:18px 26px;font:11px Arial;color:#9aa3b2;">由 paper-radar 自动生成与维护</td></tr>
</table></body></html>'''

ROW_TPL = '''<tr><td style="padding:16px 26px;border-bottom:1px solid #eef0f3;">
  <a href="archive/__FILE__" style="font:bold 16px 'Microsoft YaHei',Arial;color:#15233b;text-decoration:none;">__DATE__</a>
  <div style="font:13px/1.6 'Microsoft YaHei',Arial;color:#55607a;padding-top:6px;">__N__ 篇 · __FIRST__</div>
</td></tr>'''


def _load_meta():
    if os.path.exists(META):
        try:
            return json.load(open(META, encoding='utf-8'))
        except Exception:
            return []
    return []


def main():
    os.makedirs(settings.ARCHIVE_DIR, exist_ok=True)
    with open('picks.json', encoding='utf-8') as f:
        picks = json.load(f)
    today = date.today().isoformat()
    fname = today + '.html'

    rows = ''.join(render.paper_row(i, p) for i, p in enumerate(picks, 1))
    issue = (ISSUE_TPL
             .replace('__ROWS__', rows)
             .replace('__DATE__', today)
             .replace('__N__', str(len(picks)))
             .replace('__TH__', str(settings.SCORE_THRESHOLD)))
    with open(os.path.join(settings.ARCHIVE_DIR, fname), 'w', encoding='utf-8') as f:
        f.write(issue)

    meta = _load_meta()
    meta = [m for m in meta if m.get('file') != fname]
    first = picks[0]['title'] if picks else '（本期无精选）'
    meta.insert(0, {'date': today, 'file': fname, 'n': len(picks), 'first': first})
    meta = meta[:60]
    with open(META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    rows_html = ''.join(
        ROW_TPL.replace('__FILE__', m['file'])
               .replace('__DATE__', m['date'])
               .replace('__N__', str(m['n']))
               .replace('__FIRST__', render.esc(m['first']))
        for m in meta)
    with open(os.path.join(settings.DOCS_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(INDEX_TPL.replace('__LIST__', rows_html))

    print('网页归档完成：docs/archive/%s，归档首页 docs/index.html（共 %d 期）' % (fname, len(meta)))


if __name__ == '__main__':
    main()
