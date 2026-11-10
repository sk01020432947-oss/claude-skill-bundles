#!/usr/bin/env python3
"""유홍준식 퇴고 기계 점검. 사용: python3 yhj_check.py 원고.md  (또는 stdin)
잡는 것: 접속사로 시작하는 문장, '~하였는데/~했는데' 늘어짐, 형용사 앞 강조부사,
너무 긴 문장, '~에 있어서/~함에 있어' 같은 '의'로 줄일 수 있는 군더더기.
판단은 사람이 한다. 이 스크립트는 후보만 표시한다.
"""
import re, sys

CONJ = ("그리고", "그래서", "그러나", "그런데", "하지만", "따라서", "또한", "그러므로", "하여튼", "아무튼", "그리하여", "게다가")
INTENS = r"(너무|참으로|정말|매우|아주|굉장히|무척|진짜)\s*\S+"
NEUNDE = r"(했는데|하였는데|였는데|이었는데|었는데|았는데)"
WORDY = r"(에 있어서|함에 있어|에 대한|에 관한|하는 것이다|것이라고 할 수 있다)"
LONG = 80  # ponytail: 글자수 기준 단순 휴리스틱, 어절 기준이 필요하면 바꿀 것


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?。])\s+|\n+", text) if s.strip()]


def check(text):
    out = []
    for i, s in enumerate(sentences(text), 1):
        if s.startswith(CONJ):
            out.append((i, "접속사로 시작", s))
        if re.search(NEUNDE, s):
            out.append((i, "~했는데 늘어짐 → 끊기", s))
        if re.search(INTENS, s):
            out.append((i, "강조부사 → 이미지로 대체", s))
        if re.search(WORDY, s):
            out.append((i, "군더더기 → '의'·짧게", s))
        if len(s) > LONG:
            out.append((i, f"긴 문장({len(s)}자)", s))
    return out


def demo():
    r = check("그래서 우리는 갔다. 날씨가 좋았는데 비가 왔다. 정말 아름다웠다. 짧다.")
    kinds = [k for _, k, _ in r]
    assert "접속사로 시작" in kinds and "~했는데 늘어짐 → 끊기" in kinds
    assert "강조부사 → 이미지로 대체" in kinds
    assert all(n != 4 for n, _, _ in r), "짧은 문장은 통과해야 함"


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        demo(); print("ok"); sys.exit()
    text = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    hits = check(text)
    for n, k, s in hits:
        print(f"[{n:>3}] {k}: {s[:70]}")
    print(f"— 후보 {len(hits)}건. 다음 단계: 소리 내어 읽기, 그다음 남에게 읽어주기.")
