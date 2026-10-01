# -*- coding: utf-8 -*-
"""
第 2 关 · AI 当编辑
读取 papers.json，调用 DeepSeek，给每篇论文：
  - score：0-10（依据研究兴趣，用于筛选与排序）
  - keep：是否值得读
  - cn_title：直白易懂的中文标题
  - cn_summary：通俗准确的中文摘要
  - reason：推荐理由 / 为什么值得读
  - connection：与研究方向的关联思考
  - ratings：四维度 1-5 分（方向相关性 / 创新与贡献 / 方法严谨性 / 实践启发性）
然后按分数排序，筛出高分的，存 ranked.json（全部）和 picks.json（精选）。
"""
import json
import urllib.request
import settings

API_URL = 'https://api.deepseek.com/chat/completions'
MODEL = 'deepseek-chat'

# 评分维度：(JSON 短键, 中文名)
RATING_FIELDS = [
    ('rel', '方向相关性'),
    ('nov', '创新与贡献'),
    ('rig', '方法严谨性'),
    ('imp', '实践启发性'),
]

SYSTEM_PROMPT = (
    '你是一位资深的人机交互与数字文化遗产领域科研编辑，擅长把英文论文讲得直白、通俗，'
    '面向的读者做的是「生成式AI × 交互/游戏化叙事 × 非物质文化遗产现代化传播」的交叉研究与设计实践。'
    '我会给你一批候选论文，每篇有编号、英文标题、英文摘要，可能标注了发表会场（venue）。'
    '请依据用户的研究兴趣，对每篇完成：\n'
    '1) score：0-10 整数，10=高度相关且质量很高；CHI、CHI PLAY、UIST、CSCW、DiGRA、ICIDS、FDG、DIS、IUI、ISMAR、ACL、AAAI、SIGGRAPH，'
    '以及 ACM JOCCH、Games and Culture、International Journal of Heritage Studies 等的论文可适当上浮；\n'
    '2) keep：当且仅当 score>=7、确实值得读时为 true；\n'
    '3) cn_title：把标题翻译成直白、易懂的中文，不要生硬直译，让人一眼看懂这篇在做什么；\n'
    '4) cn_summary：中文摘要，2-4 句，准确但通俗，先说做了什么、再说关键发现或结果，不堆砌术语；\n'
    '5) reason：推荐理由，1-2 句，说明亮点和为什么值得读；\n'
    '6) connection：关联思考，2-3 句，具体说明它对用户「生成式AI×交互/游戏化叙事×非遗传播」的研究或设计实践有什么可借鉴之处；\n'
    '7) ratings：四个维度各打 1-5 的整数分——rel=与研究方向的相关性，nov=创新性与贡献，rig=方法与论证的严谨性，imp=对实践的启发性。\n'
    '严格只返回 JSON，不要多余文字，格式：\n'
    '{"results":[{"i":1,"score":8,"keep":true,"cn_title":"直白中文标题","cn_summary":"中文摘要",'
    '"reason":"推荐理由","connection":"关联思考","ratings":{"rel":4,"nov":4,"rig":4,"imp":5}}]}'
)


def load_papers():
    with open('papers.json', encoding='utf-8') as f:
        return json.load(f)


def build_user_prompt(papers, offset=0):
    lines = ['【用户研究兴趣】', settings.RESEARCH_INTEREST, '', '【候选论文】']
    for j, p in enumerate(papers):
        idx = offset + j + 1
        lines.append('[%d] 标题：%s' % (idx, p['title']))
        if p.get('venue'):
            lines.append('    会场：%s（%s）' % (p['venue'], p.get('source', '')))
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
        'max_tokens': 8192,
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
    print('共 %d 篇候选，分批调用 DeepSeek 打分、翻译并撰写导读……' % len(papers))
    results = {}
    CHUNK = 25
    for start in range(0, len(papers), CHUNK):
        batch = papers[start:start + CHUNK]
        print('  正在处理第 %d-%d 篇……' % (start + 1, start + len(batch)))
        verdict = call_deepseek(build_user_prompt(batch, start))
        for r in verdict.get('results', []):
            results[r['i']] = r

    ranked = []
    for idx, p in enumerate(papers, 1):
        r = results.get(idx, {})
        rt = r.get('ratings', {}) or {}
        item = dict(p)
        item['score'] = int(r.get('score', 0))
        item['keep'] = bool(r.get('keep', False))
        item['cn_title'] = r.get('cn_title', '')
        item['cn_summary'] = r.get('cn_summary', '')
        item['reason'] = r.get('reason', '')
        item['connection'] = r.get('connection', '')
        item['ratings'] = {k: int(rt.get(k, 0) or 0) for k, _ in RATING_FIELDS}
        ranked.append(item)

    ranked.sort(key=lambda x: x['score'], reverse=True)
    picks = [x for x in ranked if x['score'] >= settings.SCORE_THRESHOLD][:settings.MAX_PICK]

    with open('ranked.json', 'w', encoding='utf-8') as f:
        json.dump(ranked, f, ensure_ascii=False, indent=2)
    with open('picks.json', 'w', encoding='utf-8') as f:
        json.dump(picks, f, ensure_ascii=False, indent=2)

    print('\nAI 精选出 %d 篇（阈值 %d 分）：\n' % (len(picks), settings.SCORE_THRESHOLD))
    for i, p in enumerate(picks, 1):
        print('%d. [%d分] %s' % (i, p['score'], p.get('cn_title') or p['title']))
        print('   ' + p['cn_summary'])
        print('   ' + p['abs_url'])


if __name__ == '__main__':
    main()
