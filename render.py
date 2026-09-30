# -*- coding: utf-8 -*-
"""
第 3 关 · 排邮件
读取 picks.json，生成一封美观、可直接发送的 HTML 邮件 email.html。
采用表格 + 内联样式，兼容 QQ / Gmail / Outlook 等常见邮箱。
"""
import json
import html
from datetime import date


def esc(s):
    return html.escape(str(s if s is not None else ''))


def score_color(score):
    if score >= 9:
        return '#c2410c'   # 高相关：橙
    if score == 8:
        return '#1d4ed8'   # 很相关：蓝
    return '#475569'       # 值得读：石板灰


def paper_row(i, p):
    authors = p.get('authors', [])
    au_text = '、'.join(authors[:3]) + (' 等' if len(authors) > 3 else '')
    col = score_color(p['score'])
    pdf_link = p.get('pdf_url') or p.get('abs_url')
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
          <div style="font:bold 16px/1.45 'Segoe UI','Microsoft YaHei',Arial;color:#15233b;">%s</div>
          <div style="font:13.5px/1.65 'Microsoft YaHei',Arial;color:#33415c;padding-top:7px;">%s</div>
          <div style="font:12px/1.5 Arial;color:#8a93a6;padding-top:7px;">%s · %s</div>
          <div style="padding-top:13px;">
            <a href="%s" style="display:inline-block;background:#14345c;color:#fff;
               text-decoration:none;font:bold 12px Arial;padding:10px 15px;border-radius:6px;
               margin-right:8px;">查看原文</a>
            <a href="%s" style="display:inline-block;border:1px solid #14345c;color:#14345c;
               text-decoration:none;font:bold 12px Arial;padding:9px 15px;border-radius:6px;">下载 PDF</a>
          </div>
        </td>
      </tr></table>
    </td></tr>
  </table>
</td></tr>''' % (col, p['score'], esc(p['title']), esc(p.get('cn_summary', '')),
                  esc(au_text), esc(p.get('published', '')),
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
  <table role="presentation" width="680" cellpadding="0" cellspacing="0"
         style="max-width:680px;background:#ffffff;border-radius:14px;overflow:hidden;">
    <tr><td style="background:#14345c;padding:26px 24px;">
      <div style="font:bold 23px 'Microsoft YaHei',Arial;color:#fff;">论文雷达 · HCI 周报</div>
      <div style="font:13px Arial;color:#cdd9ec;padding-top:9px;line-height:1.6;">
        %s 出刊 · 本期精选 %d 篇（DeepSeek 依据你的研究兴趣打分筛选）</div>
    </td></tr>
    <tr><td style="height:20px;"></td></tr>
    %s
    <tr><td style="padding:6px 24px 26px;font:11px/1.7 Arial;color:#9aa3b2;">
      本邮件由 paper-radar 自动生成：数据来自 arXiv，DeepSeek 打分并撰写中文摘要，分数 &ge; %d 入选。
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
