#!/usr/bin/env python3
"""캐릭터 스타일 프롬프트 110개 검색·출력.
사용: python3 find.py            # 전체 목록(번호·제목)
      python3 find.py 낙서       # 카테고리(한글/영문 키) 목록
      python3 find.py 낙서 3     # 프롬프트 전문 출력
      python3 find.py -s 도장    # 제목·본문 검색
"""
import json, sys, os
DATA = json.load(open(os.path.join(os.path.dirname(__file__), 'prompts.json'), encoding='utf-8'))
CATS = {c['ko']: c for c in DATA} | {c['key']: c for c in DATA} | {c['en'].lower(): c for c in DATA}

def show(c, it): print(f"[{c['ko']} {c['en']} {it['no']:02d}] {it['title']}\n\n{it['prompt']}\n")

a = sys.argv[1:]
if not a:
    for c in DATA:
        print(f"## {c['ko']} {c['en']} — {c['desc']}")
        for it in c['items']: print(f"  {it['no']:02d} {it['title']}")
elif a[0] == '-s':
    q = ' '.join(a[1:])
    for c in DATA:
        for it in c['items']:
            if q in it['title'] or q in it['prompt']: show(c, it)
else:
    c = CATS.get(a[0].lower())
    if not c: sys.exit(f"카테고리 없음: {a[0]} (사용 가능: {', '.join(x['ko'] for x in DATA)})")
    if len(a) == 1:
        for it in c['items']: print(f"  {it['no']:02d} {it['title']}")
    else:
        it = next((i for i in c['items'] if i['no'] == int(a[1])), None)
        show(c, it) if it else sys.exit("번호는 1~10")
