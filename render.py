# -*- coding: utf-8 -*-
"""
第 3 关 · 排邮件
读取 picks.json，生成美观、可直接发送的 HTML 邮件 email.html。
每篇含：直白中文标题 + 英文原题、中文导读（在上）+ 英文原文摘要（在下）、
四维度星级评分、推荐理由、与研究方向的关联思考、原文/PDF 链接。
采用表格 + 内联样式，兼容 QQ / Gmail / Outlook。
"""
import json
import html
from datetime import date

# 评分维度（短键, 中文名），顺序与 rank.py 一致
RATING_LABELS = [
    ('rel', '方向相关性'),
    ('nov', '创新与贡献'),
    ('rig', '方法严谨性'),
    ('imp', '实践启发性'),
]


def esc(s):
    return html.escape(str(s if s is not None else ''))


def score_color(score):
    if score >= 9:
        return '#c2410c'
    if score == 8:
        return '#1d4ed8'
    return '#475569'


def stars(n):
    n = max(0, min(5, int(n or 0)))
    return '<span style="color:#e8832a;letter-spacing:1px;">' + ('●' * n) + \
           ('<span style="color:#d7dce3;">' + ('○' * (5 - n)) + '</span>') + '</span>'


def rating_block(p):
    ratings = p.get('ratings', {}) or {}
    cells = []
    vals = []
    for k, label in RATING_LABELS:
        v = int(ratings.get(k, 0) or 0)
        if v:
            vals.append(v)
        cells.append(
            '<td style="width:25%%;padding:6px 4px;text-align:center;">'
            '<div style="font:11.5px "Microsoft YaHei",Arial;color:#64708a;">%s</div>'
            '<div style="font-size:13px;padding-top:3px;">%s</div>'
            '<div style="font:bold 12px Arial;color:#33415c;padding-top:2px;">%d/5</div></td>'
            % (label, stars(v), v))
    avg = ('%.1f' % (sum(vals) / len(vals))) if vals else '-'
    return '''
      <table role="presentation" width="100%%" cellpadding="0" cellspacing="0"
             style="background:#f6f8fb;border:1px solid #e8edf3;border-radius:8px;margin-top:12px;">
        <tr>%s</tr></table>
      <div style="font:12px/1.6 Arial;color:#8a93a6;padding-top:7px;">学术价值综合评分：
        <span style="font:bold 14px 'Segoe UI',Arial;color:#c2410c;">%s</span> / 5
        （另：整体相关度 %d/10）</div>''' % (''.join(cells), avg, p['score'])


def labeled_box(label, body, bg, bar):
    if not body:
        return ''
    return '''
      <div style="margin-top:12px;background:%s;border-radius:8px;padding:11px 13px;">
        <div style="font:bold 12.5px 'Microsoft YaHei',Arial;color:%s;padding-bottom:4px;">%s</div>
        <div style="font:13.5px/1.7 'Microsoft YaHei',Arial;color:#33415c;">%s</div>
      </div>''' % (bg, bar, label, esc(body))


def paper_row(i, p):
    authors = p.get('authors', [])
    au_text = '、'.join(authors[:3]) + (' 等' if len(authors) > 3 else '')
    col = score_color(p['score'])
    pdf_link = p.get('pdf_url') or p.get('abs_url')
    venue = p.get('venue') or p.get('source') or ''
    cn_title = p.get('cn_title') or p['title']
    return '''
<tr><td style="padding:0 24px 16px 24px;">
  <table role="presentation" width="100%%" cellpadding="0" cellspacing="0"
         style="border:1px solid #e6e8ec;border-radius:10px;background:#fff;">
    <tr><td style="padding:18px 20px;">
      <table role="presentation" width="100%%" cellpadding="0" cellspacing="0"><tr>
        <td style="width:46px;vertical-align:top;">
          <div style="width:46px;height:46px;border-radius:50%%;background:%s;color:#fff;
                      font:bold 17px Arial;line-height:46px;text-align:center;">%d</div>
        </td>
        <td style="padding-left:14px;vertical-align:top;">
          <div style="font:bold 17px/1.45 'Segoe UI','Microsoft YaHei',Arial;color:#15233b;">%s</div>
          <div style="font:italic 12px/1.5 Arial;color:#8a93a6;padding-top:5px;">%s</div>
          <div style="font:12px/1.5 Arial;color:#8a93a6;padding-top:7px;">%s · %s · %s</div>
        </td>
      </tr></table>
      %s
      <div style="margin-top:14px;">
        <div style="font:bold 12.5px 'Microsoft YaHei',Arial;color:#1d4ed8;padding-bottom:4px;">中文导读</div>
        <div style="font:13.5px/1.75 'Microsoft YaHei',Arial;color:#28364c;">%s</div>
      </div>
      <div style="margin-top:12px;">
        <div style="font:bold 12.5px 'Microsoft YaHei',Arial;color:#8a93a6;padding-bottom:4px;">原文摘要 · Abstract</div>
        <div style="font:12.5px/1.7 Arial;color:#788296;">%s</div>
      </div>
      %s
      %s
      <div style="padding-top:14px;">
        <a href="%s" style="display:inline-block;background:#14345c;color:#fff;
           text-decoration:none;font:bold 12px Arial;padding:10px 15px;border-radius:6px;margin-right:8px;">查看原文</a>
        <a href="%s" style="display:inline-block;border:1px solid #14345c;color:#14345c;
           text-decoration:none;font:bold 12px Arial;padding:9px 15px;border-radius:6px;">下载 PDF</a>
      </div>
    </td></tr>
  </table>
</td></tr>''' % (
        col, p['score'], esc(cn_title), esc(p['title']),
        esc(au_text), esc(venue), esc(p.get('published', '')),
        rating_block(p),
        esc(p.get('cn_summary', '')),
        esc(p.get('summary', '')),
        labeled_box('推荐理由 · 为什么值得读', p.get('reason', ''), '#fff5ec', '#c2410c'),
        labeled_box('与你研究的关联思考', p.get('connection', ''), '#eef4ff', '#1d4ed8'),
        esc(p.get('abs_url', '')), esc(pdf_link))


def render(picks, threshold):
    today = date.today().isoformat()
    rows = ''.join(paper_row(i, p) for i, p in enumerate(picks, 1))
    return '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:26px;background:#eef1f5;">
<table role="presentation" width="100%%" cellpadding="0" cellspacing="0">
<tr><td align="center">
  <table role="presentation" width="700" cellpadding="0" cellspacing="0"
         style="max-width:700px;background:#ffffff;border-radius:14px;overflow:hidden;">
    <tr><td style="background:#14345c;padding:26px 24px;">
      <div style="font:bold 23px 'Microsoft YaHei',Arial;color:#fff;">论文雷达 · AI×叙事×非遗周报</div>
      <div style="font:13px Arial;color:#cdd9ec;padding-top:9px;line-height:1.6;">
        %s 出刊 · 本期精选 %d 篇（含中文导读、原文摘要、学术价值评分、推荐理由与关联思考）</div>
    </td></tr>
    <tr><td style="height:20px;"></td></tr>
    %s
    <tr><td style="padding:6px 24px 26px;font:11px/1.7 Arial;color:#9aa3b2;">
      本邮件由 paper-radar 自动生成：数据来自 arXiv + OpenAlex，DeepSeek 打分、翻译并撰写导读，整体相关度 &ge; %d 入选。
      “查看原文”指向摘要页，“下载 PDF”仅开放获取论文可直接下载，其余请用机构权限访问。
    </td></tr>
  </table>
</td></tr>
</table>
</body></html>''' % (today, len(picks), rows, threshold)


def main():
    with open('picks.json', encoding='utf-8') as f:
        picks = json.load(f)
    import settings
    html_text = render(picks, settings.SCORE_THRESHOLD)
    with open('email.html', 'w', encoding='utf-8') as f:
        f.write(html_text)
    print('已生成 email.html，共 %d 篇。' % len(picks))


if __name__ == '__main__':
    main()
