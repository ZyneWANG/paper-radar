# -*- coding: utf-8 -*-
"""
第 6 关 · 推送到飞书
用飞书群「自定义机器人」Webhook，把精选论文做成 interactive 卡片。
- 安全设置选「签名校验」时填 settings.FEISHU_SECRET，自动计算签名；
- 选「关键词」时 FEISHU_SECRET 留空，只要卡片标题含约定关键词即可；
全程只用标准库。
"""
import json
import time
import hmac
import base64
import hashlib
import urllib.request
from datetime import date

import settings


def make_sign(secret, timestamp):
    string_to_sign = '%d\n%s' % (timestamp, secret)
    digest = hmac.new(string_to_sign.encode('utf-8'),
                      digestmod=hashlib.sha256).digest()
    return base64.b64encode(digest).decode('utf-8')


def build_card(picks):
    today = date.today().isoformat()
    elements = [
        {"tag": "div", "text": {"tag": "lark_md",
                                "content": "本期精选 **%d** 篇 · %s\n数据：arXiv + OpenAlex，DeepSeek 打分" % (len(picks), today)}},
        {"tag": "hr"},
    ]
    for p in picks:
        venue = p.get('venue') or p.get('source') or ''
        title = p['title'].replace('[', '(').replace(']', ')')
        link = p.get('abs_url') or ''
        md = "**[%d分] [%s](%s)**\n%s · %s\n%s" % (
            p['score'], title, link, venue, p.get('published', ''),
            p.get('cn_summary', ''))
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": md}})
        elements.append({"tag": "hr"})
    elements.append({"tag": "note", "elements": [
        {"tag": "plain_text",
         "content": "paper-radar 自动推送 · 标题可点查看原文，PDF 请用机构权限或开放获取链接"}]})
    return {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": "论文雷达 · AI×叙事×非遗周报"},
                "template": "blue",
            },
            "elements": elements,
        },
    }


def send_card(card):
    # 飞书偶发返回签名/时间错误（19021），做最多 3 次重试，每次重新取时间戳并签名
    last = None
    for attempt in range(3):
        url = settings.FEISHU_WEBHOOK
        if settings.FEISHU_SECRET:
            ts = int(time.time())
            url = '%s?timestamp=%d&sign=%s' % (
                url, ts, make_sign(settings.FEISHU_SECRET, ts))
        body = json.dumps(card).encode('utf-8')
        req = urllib.request.Request(
            url, data=body,
            headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                r = json.loads(resp.read().decode('utf-8'))
            if r.get('StatusCode', r.get('code', 0)) in (0, None):
                if attempt:
                    print('飞书第 %d 次尝试成功。' % (attempt + 1))
                return r
            last = r
        except Exception as e:
            last = {'error': str(e)}
        time.sleep(2)
    return last if last is not None else {'code': -1}


def main():
    if not settings.FEISHU_WEBHOOK:
        print('未配置飞书 Webhook，跳过飞书推送。')
        return
    with open('picks.json', encoding='utf-8') as f:
        picks = json.load(f)
    if not picks:
        print('本期没有精选论文，不推飞书。')
        return
    r = send_card(build_card(picks))
    if r.get('StatusCode', r.get('code', 0)) in (0, None):
        print('飞书推送成功！')
    else:
        print('飞书返回：', r)


if __name__ == '__main__':
    main()
