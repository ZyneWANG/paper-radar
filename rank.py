# -*- coding: utf-8 -*-
"""
第 2 关 · AI 当编辑
读取 papers.json，调用 DeepSeek，给每篇论文：
  - 打分 0-10（依据你的研究兴趣）
  - 判断是否值得读（keep）
  - 写一句中文摘要
然后按分数排序，筛出高分的，存 ranked.json（全部打分）和 picks.json（精选）。
"""
import json
import urllib.request
import settings

API_URL = 'https://api.deepseek.com/chat/completions'
MODEL = 'deepseek-chat'

SYSTEM_PROMPT = (
    '你是一位资深的人机交互（HCI）领域科研编辑。'
    '我会给你一批候选论文，每篇有编号、英文标题、英文摘要。'
    '请依据用户的研究兴趣，判断每篇的相关性与质量：\n'
    '1) score：0-10 的整数，10 表示高度相关且质量很高；\n'
    '2) keep：当且仅当 score>=7、确实值得用户阅读时为 true；\n'
    '3) cn：一句不超过 40 个汉字的中文摘要，说清“做了什么 + 核心发现”。\n'
    '严格只返回 JSON，不要有多余文字，格式：\n'
    '{"results":[{"i":1,"score":8,"keep":true,"cn":"中文一句话"}]}'
)


def load_papers():
    with open('papers.json', encoding='utf-8') as f:
        return json.load(f)


def build_user_prompt(papers):
    lines = ['【用户研究兴趣】', settings.RESEARCH_INTEREST, '', '【候选论文】']
    for idx, p in enumerate(papers, 1):
        lines.append('[%d] 标题：%s' % (idx, p['title']))
        lines.append('    摘要：%s' % p['summary'][:700])
    return '\n'.join(lines)


def call_deepseek(user_prompt):
    key = (settings.DEEPSEEK_API_KEY or '').strip()
    if (not key) or ('粘贴' in key) or (not key.startswith('sk-')):
        raise SystemExit('还没填好 DeepSeek Key：请打开 config.py，把 key 填进去并保存。')
    payload = {
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_prompt},
        ],
        'response_format': {'type': 'json_object'},
        'temperature': 0.2,
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json',
                 'Authorization': 'Bearer ' + key},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    content = data['choices'][0]['message']['content']
    return json.loads(content)


def main():
    papers = load_papers()
    if not papers:
        raise SystemExit('papers.json 是空的，先运行 python fetch.py。')
    print('共 %d 篇候选，正在调用 DeepSeek 打分、写中文摘要……' % len(papers))
    verdict = call_deepseek(build_user_prompt(papers))
    results = {r['i']: r for r in verdict.get('results', [])}

    ranked = []
    for idx, p in enumerate(papers, 1):
        r = results.get(idx, {})
        item = dict(p)
        item['score'] = int(r.get('score', 0))
        item['keep'] = bool(r.get('keep', False))
        item['cn_summary'] = r.get('cn', '')
        ranked.append(item)

    ranked.sort(key=lambda x: x['score'], reverse=True)
    picks = [x for x in ranked if x['score'] >= settings.SCORE_THRESHOLD][:settings.MAX_PICK]

    with open('ranked.json', 'w', encoding='utf-8') as f:
        json.dump(ranked, f, ensure_ascii=False, indent=2)
    with open('picks.json', 'w', encoding='utf-8') as f:
        json.dump(picks, f, ensure_ascii=False, indent=2)

    print('\nAI 精选出 %d 篇（阈值 %d 分）：\n' % (len(picks), settings.SCORE_THRESHOLD))
    for i, p in enumerate(picks, 1):
        print('%d. [%d分] %s' % (i, p['score'], p['title']))
        print('   ' + p['cn_summary'])
        print('   ' + p['abs_url'])


if __name__ == '__main__':
    main()
