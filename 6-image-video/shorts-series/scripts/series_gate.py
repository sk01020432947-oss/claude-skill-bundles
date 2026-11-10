#!/usr/bin/env python3
"""Shorts 시리즈 승인 게이트: 편마다 '내가 고친 횟수'를 기록하고,
최근 N편 연속 무수정이면 '자동 발행 후보'로 표시한다. 업로드는 하지 않는다.

사용:
  series_gate.py init  <시리즈폴더> --name 설교한줄키네틱
  series_gate.py log   <시리즈폴더> <편이름> --edits 2 --note "자막 늦음"
  series_gate.py status <시리즈폴더> [--need 3]
  series_gate.py selftest
"""
import argparse, json, sys, datetime
from pathlib import Path

LEDGER = "episodes.jsonl"
SERIES_MD = """# 시리즈: {name}

## 1. 형식
- 길이: 45–60초 / 화면: 1080×1920 / 말투:
- 고정 프레임: 2줄 제목 · 섹션 칩 · 16:9 자료 박스 · 박자 자막 · 출처 줄
- 강조색: (한 가지, 한 화면에 한 번)

## 2. 제작 단계
1. 원재료 받기(자막·원문·발표문)
2. 대본 → 3. 화면 지시 → 4. 렌더(HyperFrames/Remotion) → 5. 검사 → 6. 사람 확인

## 3. 매번 확인할 검사 기준
- [ ] 모든 사실·숫자가 붙여 넣은 원문에 있다
- [ ] 첫 문장이 앞 맥락에 기대지 않는다
- [ ] 출처 줄이 있다
- [ ] 실제 회사·인물 이름을 콩트에 쓰지 않았다

## 4. 피드백 장부 (고친 내용은 slop-feedback-ledger 형식: 번호·대상·지시·이유)

## 5. 자동 발행 규칙
- 최근 {need}편을 한 번도 고치지 않았을 때만 '자동 발행 후보'. 실제 업로드는 사람이 한다.
"""


def load(d):
    p = Path(d) / LEDGER
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def streak(eps):
    n = 0
    for e in reversed(eps):
        if e["edits"] != 0:
            break
        n += 1
    return n


def gate(eps, need):
    s = streak(eps)
    return s, s >= need


def cmd_init(a):
    d = Path(a.dir); d.mkdir(parents=True, exist_ok=True)
    md = d / "SERIES.md"
    if not md.exists():
        md.write_text(SERIES_MD.format(name=a.name, need=a.need), encoding="utf-8")
    (d / LEDGER).touch()
    print(f"준비됨: {md}")


def cmd_log(a):
    if a.edits < 0:
        sys.exit("edits는 0 이상")
    rec = {"episode": a.episode, "edits": a.edits, "note": a.note,
           "at": datetime.datetime.now().isoformat(timespec="seconds")}
    with open(Path(a.dir) / LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    cmd_status(a)


def cmd_status(a):
    eps = load(a.dir)
    s, ok = gate(eps, a.need)
    print(f"편수 {len(eps)} · 최근 무수정 연속 {s}/{a.need} · "
          + ("자동 발행 후보 (업로드는 직접)" if ok else "사람 확인 계속"))


def selftest():
    e = lambda n: {"episode": "x", "edits": n}
    assert gate([], 3) == (0, False)
    assert gate([e(0), e(0), e(0)], 3) == (3, True)
    assert gate([e(0), e(0), e(0), e(1)], 3) == (0, False)   # 마지막에 고치면 리셋
    assert gate([e(2), e(0), e(0), e(0), e(0)], 4) == (4, True)
    print("selftest OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    for c in ("init", "log", "status"):
        p = sp.add_parser(c); p.add_argument("dir"); p.add_argument("--need", type=int, default=3)
        if c == "init": p.add_argument("--name", required=True)
        if c == "log":
            p.add_argument("episode"); p.add_argument("--edits", type=int, required=True)
            p.add_argument("--note", default="")
    sp.add_parser("selftest")
    a = ap.parse_args()
    {"init": cmd_init, "log": cmd_log, "status": cmd_status,
     "selftest": lambda _: selftest()}[a.cmd](a)
