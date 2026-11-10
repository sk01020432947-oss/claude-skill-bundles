"""기법 분류 체계(technique-taxonomy.md)의 ◆ 항목을 숫자로 계산한다.

사용:
    python metrics.py <파일>                 # 한 편 측정
    python metrics.py <원문> --vs <내글>      # 두 편 대조
    python metrics.py <파일> --json          # JSON만 출력

표준 라이브러리만 쓴다. 형태소 분석기는 쓰지 않고 정규식·접미사 사전으로 근사한다.
근사이므로 절대값이 아니라 **두 글의 차이**를 보는 데 쓴다.
"""
import re, sys, json, statistics as st

# ── 사전 ──────────────────────────────────────────────
WINNER = ['좋다', '좋은', '나쁘다', '나쁜', '예쁘다', '예쁜', '이상하다', '이상한',
          '비슷하다', '비슷한', '다르다', '큰', '작은', '많은', '대단하다']
VAGUE = ['여러', '일부', '상당한', '상당수', '적절한', '다양한', '많은', '약간', '어느 정도']
EMOTION = ['슬펐다', '슬프다', '기뻤다', '기쁘다', '행복했다', '화가 났다', '외로웠다',
           '무서웠다', '설레었다', '벅찼다', '허탈했다', '뿌듯했다', '즐거웠다', '괴로웠다']
CONJ = ['그러나', '그래서', '따라서', '하지만', '그리고', '그런데', '또한', '즉', '결국', '물론']
HANJA_SUFFIX = ['하다', '되다', '적이다']
HANJA_VERBS = ['제고', '도출', '활용', '소요', '상기', '개진', '기인', '산재', '명시', '상이',
               '수행', '초래', '저하', '증대', '감소', '실시', '진행', '완료', '검토', '수립']
SENSE = {
    '시각': ['보였다', '보이는', '빛', '색', '붉', '푸르', '희', '검', '반짝', '눈부', '어두', '밝'],
    '청각': ['소리', '들렸다', '들리는', '울렸', '조용', '시끄', '삐걱', '쿵', '속삭'],
    '촉각': ['만졌', '차가', '뜨거', '따뜻', '거칠', '부드럽', '축축', '까끌', '아팠'],
    '후각': ['냄새', '향', '구수', '비릿', '퀴퀴'],
    '미각': ['맛', '달았', '짰', '썼', '시큼', '싱거'],
}
JUDGE = ['아름다', '낡았', '멋있', '훌륭', '끔찍', '지저분', '깨끗', '더러']
HEDGE = ['것 같다', '것 같았다', '라고 볼 수 있다', '수도 있다', '듯하다', '아닐까',
         '일장일단', '경우에 따라']
ADDRESS = ['여러분', '당신', '우리는', '우리가']
MORAL = ['많은 것을 배웠', '열심히 하겠', '감사드린', '살펴본 바와 같이', '되었으면 좋겠',
         '느낄 수 있었다', '뜻깊은', '알찬']


def strip_markup(t):
    """제목·표·코드블록·목록기호를 걷어낸다. 산문만 세야 수치가 맞는다."""
    t = re.sub(r'^---\n.*?\n---\n', '', t, flags=re.S)      # frontmatter
    t = re.sub(r'```.*?```', '', t, flags=re.S)              # 코드블록
    t = re.sub(r'^\s*#{1,6}\s.*$', '', t, flags=re.M)        # 제목
    t = re.sub(r'^\s*\|.*$', '', t, flags=re.M)              # 표
    t = re.sub(r'^\s*[-*]{3,}\s*$', '', t, flags=re.M)       # 구분선
    t = re.sub(r'^\s*[-*+]\s+|^\s*\d+\.\s+|^\s*>\s?', '', t, flags=re.M)  # 목록·인용 기호
    t = re.sub(r'\*\*|__|`', '', t)                          # 강조 기호
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)           # 링크
    return re.sub(r'\n{3,}', '\n\n', t).strip()


def sentences(t):
    t = re.sub(r'\s+', ' ', t)
    return [s.strip() for s in re.split(r'(?<=[.!?。])\s+|(?<=다\.)\s+', t) if len(s.strip()) > 1]


def paragraphs(t):
    return [p.strip() for p in re.split(r'\n\s*\n', t) if p.strip()]


def count(t, words):
    return sum(t.count(w) for w in words)


def ending(s):
    s = s.rstrip('"\'”’ ').rstrip('.!?')
    for pat, name in [(r'습니다$|ㅂ니다$', '-습니다'), (r'했다$|었다$|았다$|였다$', '-다(과거)'),
                      (r'[가-힣]다$', '-다'), (r'요$', '-요'), (r'네$', '-네'), (r'지$', '-지'),
                      (r'까$|나$', '-의문'), (r'라$|자$', '-청유명령')]:
        if re.search(pat, s):
            return name
    return '체언종지' if re.search(r'[가-힣]$', s) else '기타'


def analyze(text):
    text = strip_markup(text)
    ss, pp = sentences(text), paragraphs(text)
    n = max(len(text), 1)
    L = [len(s) for s in ss] or [0]
    per100 = lambda c: round(c / n * 100, 2)

    ends = [ending(s) for s in ss]
    run = mx = 1
    for i in range(1, len(ends)):
        run = run + 1 if ends[i] == ends[i - 1] else 1
        mx = max(mx, run)

    short_run = mxs = 0
    for x in L:
        short_run = short_run + 1 if x <= 15 else 0
        mxs = max(mxs, short_run)

    alternation = sum(1 for i in range(1, len(L)) if L[i - 1] >= 40 and L[i] <= 15)
    commas = text.count(',')
    senses = {k: count(text, v) for k, v in SENSE.items()}

    m = {
        '_기본': {
            '글자수': n, '문장수': len(ss), '문단수': len(pp),
        },
        'L2-01 문장길이': {
            '평균': round(st.mean(L), 1),
            '표준편차': round(st.pstdev(L), 1) if len(L) > 1 else 0,
            '최장': max(L), '60자초과': sum(1 for x in L if x > 60),
        },
        'L2-02 장단교차': {'긴→짧은 전환': alternation},
        'L2-03 복문': {'연결어미/문장': round(count(text, ['며 ', '고 ', '는데', '지만', '면서']) / max(len(ss), 1), 2)},
        'L2-04 종결어미': {'종류수': len(set(ends)), '최장연속': mx,
                        '분포': dict(sorted({e: ends.count(e) for e in set(ends)}.items(), key=lambda x: -x[1])[:4])},
        'L2-05 피동': {'피동표현/100자': per100(count(text, ['되었', '되는', '되며', '어졌', '아졌', '에 의해', '되어지']))},
        'L2-07 명사형종결': {'개수': sum(1 for e in ends if e == '체언종지')},
        'L2-10 접속사': {'개/100자': per100(count(text, CONJ))},
        'L2-11 주어반복': {'나는·저는': count(text, ['나는 ', '저는 ', '내가 ', '제가 '])},
        'L2-12 부호': {'쉼표': commas, '줄표': text.count('—') + text.count('–'),
                     '괄호': text.count('('), '느낌표': text.count('!'),
                     '말줄임': text.count('...') + text.count('…'), '물결': text.count('~')},
        'L3-01 문단길이': {'문장/문단': round(len(ss) / max(len(pp), 1), 1)},
        'L3-07 한줄문단': {'개수': sum(1 for p in pp if len(sentences(p)) == 1)},
        'L1-02 승자독식': {'개/100자': per100(count(text, WINNER))},
        'L1-03 한자어': {'추정 한자동사': count(text, HANJA_VERBS)},
        'L1-05 감각어': senses,
        'L1-06 부사': {'개/100자': per100(count(text, ['정말', '너무', '매우', '굉장히', '진짜', '엄청', '막 ', '아주']))},
        'L1-07 추상명사': {'-성/-화/-적': len(re.findall(r'[가-힣]{1,4}(?:성|화|적)(?:을|를|이|가|은|는|의|에)', text))},
        'L1-09 흐린수량': {'개수': count(text, VAGUE), '숫자표현': len(re.findall(r'\d', text))},
        'L5-01 인칭': {'1인칭 표지': count(text, ['나는', '내가', '나의', '저는', '제가'])},
        'L5-02 시제': {'과거형': len(re.findall(r'(?:었|았|였)다', text)),
                     '현재형': len(re.findall(r'[가-힣](?:ㄴ다|는다)(?=[.\s])', text))},
        'L5-05 유보': {'개수': count(text, HEDGE)},
        'L5-07 어조': {'경어체': text.count('습니다') + text.count('입니다'),
                     '평어체': len(re.findall(r'다\.', text))},
        'L5-10 대화': {'따옴표쌍': text.count('"') // 2 + text.count('“')},
        'L6-01 비유': {'직유(처럼/같이)': count(text, ['처럼', '같이', '듯이', '마냥'])},
        'L6-06 판단어': {'개수': count(text, JUDGE)},
        'L7-05 질문': {'물음표': text.count('?')},
        'L7-10 호명': {'개수': count(text, ADDRESS)},
        'L8-04 호흡': {'쉼표간 평균자수': round(n / max(commas, 1))},
        'L8-06 끊어치기': {'15자이하 최장연속': mxs},
        'L9-02 감정어': {'개수': count(text, EMOTION)},
        'L9-03 과잉': {'느낌표+물결+강조부사': text.count('!') + text.count('~') + count(text, ['정말', '너무', '매우'])},
        'L10-02 도입': {'첫문단 비율%': round(len(pp[0]) / n * 100, 1) if pp else 0},
        'L10-05 마지막문장': {'글자수': L[-1] if L else 0},
        'L10-06 교훈종결': {'감지': count(' '.join(ss[-3:]) if ss else '', MORAL)},
    }
    return m


def flat(m, prefix=''):
    out = {}
    for k, v in m.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                if isinstance(v2, dict):
                    continue
                out[f'{k} · {k2}'] = v2
        else:
            out[k] = v
    return out


def show(m, title):
    print(f'\n{"="*62}\n{title}\n{"="*62}')
    for k, v in m.items():
        print(f'{k}')
        for k2, v2 in v.items():
            print(f'   {k2:<22} {v2}')


def compare(a, b):
    fa, fb = flat(a), flat(b)
    print(f'\n{"="*72}\n{"항목":<38}{"원문":>10}{"내 글":>10}{"차이":>12}\n{"="*72}')
    for k in fa:
        x, y = fa[k], fb.get(k)
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            continue
        d = y - x
        flag = ''
        if x and abs(d) / max(abs(x), 1) > 0.4:
            flag = '  ←차이 큼'
        print(f'{k:<38}{x:>10}{y:>10}{d:>+12.1f}{flag}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    src = open(sys.argv[1], encoding='utf-8').read()
    a = analyze(src)
    if '--json' in sys.argv:
        print(json.dumps(a, ensure_ascii=False, indent=1)); sys.exit()
    if '--vs' in sys.argv:
        mine = open(sys.argv[sys.argv.index('--vs') + 1], encoding='utf-8').read()
        compare(a, analyze(mine))
    else:
        show(a, sys.argv[1])
