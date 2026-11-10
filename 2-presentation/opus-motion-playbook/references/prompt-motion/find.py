#!/usr/bin/env python3
"""Prompt Motion(prompt-motion.com, 큐레이터 @p4nthera_) 231개 항목 검색. 2026-10-07 스냅샷.
영상·프롬프트 권리는 각 제작자(url 항목). awesome-opus55에 없는 필드: stack·iterations·effort·type(Skill).
예) python3 find.py -s remotion -n 5
    python3 find.py -c 설명·교육 --new        # awesome475에 없는 것만
    python3 find.py --skill                    # 설치형 스킬 4개
    python3 find.py --stats
"""
import argparse, collections, json, os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entries.json")
CATS = ["쇼릴·자기소개", "제품 출시·광고", "설명·교육", "역사·타임라인", "이야기·단편", "음악·가사", "게임·인터랙티브·3D", "레시피", "기타"]

def search(rows, cat=None, stack=None, it=None, kw=None, new=False, skill=False):
    out = []
    for r in rows:
        if cat and r["cat"] != cat: continue
        if stack and stack.lower() not in r["stack"].lower(): continue
        if it and it.lower() not in r["iterations"].lower(): continue
        if kw and kw.lower() not in (r["prompt"] + " " + r["title"]).lower(): continue
        if new and r["in_awesome475"]: continue
        if skill and r["type"] != "Skill": continue
        out.append(r)
    return sorted(out, key=lambda r: -len(r["prompt"]))  # 긴(구체적) 프롬프트 먼저

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--cat", choices=CATS)
    ap.add_argument("-s", "--stack", help="remotion hyperframes html three.js playwright manim ...")
    ap.add_argument("-i", "--iter", help="one-shot / few / many")
    ap.add_argument("-k", "--kw")
    ap.add_argument("--new", action="store_true", help="awesome-opus55 475개에 없는 항목만")
    ap.add_argument("--skill", action="store_true")
    ap.add_argument("-n", type=int, default=10)
    ap.add_argument("--chars", type=int, default=400)
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    rows = json.load(open(DATA, encoding="utf-8"))
    if a.stats:
        for f in ("cat", "type", "stack", "iterations", "effort"):
            print(f, collections.Counter(r[f] or "-" for r in rows).most_common())
        return
    hits = search(rows, a.cat, a.stack, a.iter, a.kw, a.new, a.skill)
    print(f"{len(hits)}건")
    for r in hits[:a.n]:
        meta = " · ".join(x for x in (r["type"], r["stack"], r["iterations"], r["effort"]) if x)
        print(f"\n## {r['title']} @{r['author']} [{r['cat']}] {meta}\n{r['url']}\n{r['prompt'][:a.chars]}")
        if r.get("install"): print(f"스킬: {r['skill_summary']}\n설치: {r['install']}\n저장소: {r['repo']}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:  # self-check
        rows = json.load(open(DATA, encoding="utf-8"))
        assert len(rows) == 231
        assert len(search(rows, skill=True)) == 4
        assert all("remotion" in r["stack"].lower() for r in search(rows, stack="remotion"))
        assert len(search(rows, new=True)) == 77
        print("ok"); sys.exit()
    main()
