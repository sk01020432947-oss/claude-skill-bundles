#!/usr/bin/env python3
"""awesome-opus5-5-videos 703개 프롬프트 검색 (MIT, yihui-dev, 2026-10-13 스냅샷, 418개 Skillry 재현).
예) python3 find.py -c explainer -t svg -k timeline --full -n 5
    python3 find.py --stats
"""
import argparse, collections, json, os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos.json")

def search(rows, cat=None, tags=(), kw=None, full=False):
    out = []
    for r in rows:
        if cat and r["category"] != cat: continue
        if any(t not in r["tech_tags"] for t in tags): continue
        if full and r["prompt_partial"]: continue
        if kw and kw.lower() not in r["prompt"].lower(): continue
        out.append(r)
    return sorted(out, key=lambda r: -len(r["prompt"]))  # 긴(구체적) 프롬프트 먼저

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--cat", choices=["motion", "explainer", "3d", "interactive"])
    ap.add_argument("-t", "--tag", action="append", default=[], help="canvas svg threejs shader gsap css audio particles playable pixel ai-image webgl physics")
    ap.add_argument("-k", "--kw")
    ap.add_argument("--full", action="store_true", help="전문 공개 프롬프트만")
    ap.add_argument("-n", type=int, default=10)
    ap.add_argument("--chars", type=int, default=400)
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--since", help="추가일 이후만, 예: 2026-10-08")
    a = ap.parse_args()
    rows = json.load(open(DATA, encoding="utf-8"))
    if a.stats:
        print(collections.Counter(r["category"] for r in rows))
        print(collections.Counter(t for r in rows for t in r["tech_tags"]).most_common()); return
    if a.since: rows = [r for r in rows if r["added"] >= a.since]
    hits = search(rows, a.cat, a.tag, a.kw, a.full)
    print(f"{len(hits)}건")
    for r in hits[:a.n]:
        print(f"\n## {r['slug']} [{r['category']}] {','.join(r['tech_tags'])}{' (부분)' if r['prompt_partial'] else ''}\n{r['skillry_url'] or r['post_url']}\n{r['prompt'][:a.chars]}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:  # self-check
        rows = json.load(open(DATA, encoding="utf-8"))
        assert len(rows) == 703
        assert all("svg" in r["tech_tags"] for r in search(rows, tags=["svg"]))
        assert len(search(rows, full=True)) == 496
        print("ok"); sys.exit()
    main()
