#!/usr/bin/env python3
"""Check that a page was rebuilt in code from a concept, not pasted from it.

  check_page.py page.html [--note "footer text"] [--allow-js]
                [--concept concept.png --shot screenshot.png]   # needs Pillow
  check_page.py --selftest

Exit 1 when a hard rule fails. Numbers are listed for a human to confirm.
"""
import argparse, json, os, re, sys
from html.parser import HTMLParser

SKIP = {"script", "style", "noscript", "title", "svg"}
NUM = re.compile(r"\d[\d,.]*\s*(?:%|퍼센트|달러|만\s?원|천\s?원|원|명|배)|[$₩]\s?\d[\d,.]*")


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.text, self.scripts, self.imgs = [], [], 0, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script":
            self.scripts += 1
        if tag in ("img", "source", "video"):
            self.imgs.append(a.get("src") or a.get("srcset") or "")
        if tag not in ("img", "br", "meta", "link", "input", "source", "hr", "path", "circle", "line", "rect"):
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass

    def handle_data(self, d):
        if not SKIP & set(self.stack) and d.strip():
            self.text.append(d.strip())


def check(html, note=None, allow_js=False):
    p = P()
    p.feed(html)
    text = " ".join(p.text)
    gif = re.findall(r"[\w./%-]+\.gif\b", html, re.I)
    concept_refs = re.findall(r"[\w./%-]*(?:concept|시안)[\w./%-]*\.(?:png|jpe?g|webp)", html, re.I)
    keyframes = len(re.findall(r"@keyframes\b", html))
    fails = []
    if gif:
        fails.append(f"GIF가 페이지에 남음: {gif[:3]}")
    if concept_refs:
        fails.append(f"시안 이미지를 페이지에 그대로 씀: {concept_refs[:3]}")
    if p.scripts and not allow_js:
        fails.append(f"script 태그 {p.scripts}개 (--allow-js 없음)")
    if len(text) < 200:
        fails.append(f"실제 글자가 {len(text)}자뿐: 그림으로 처리했을 가능성")
    if keyframes == 0 and "<canvas" not in html and "animate" not in html:
        fails.append("코드 애니메이션이 없음")
    if (keyframes or "transition" in html) and "prefers-reduced-motion" not in html:
        fails.append("prefers-reduced-motion 처리가 없음")
    if note and note not in text:
        fails.append(f"필수 문구 없음: {note}")
    return {
        "fails": fails,
        "chars": len(text),
        "placeholders": text.count("[확인 필요"),
        "scripts": p.scripts,
        "keyframes": keyframes,
        "images": len(p.imgs),
        "numbers_to_confirm": sorted(set(m.group(0).strip() for m in NUM.finditer(text))),
    }


def _lab(rgb):
    def f(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = map(f, rgb)
    x, y, z = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.9505, 0.2126 * r + 0.7152 * g + 0.0722 * b, (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.089
    g3 = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return 116 * g3(y) - 16, 500 * (g3(x) - g3(y)), 200 * (g3(y) - g3(z))


def compare(concept, shot):
    """Palette distance (mean nearest ΔE76, lower is closer) and coarse layout correlation (-1..1)."""
    from PIL import Image
    a, b = Image.open(concept).convert("RGB"), Image.open(shot).convert("RGB")

    def pal(im):
        q = im.resize((200, 300)).quantize(6)
        p = q.getpalette()[:18]
        return [_lab(p[i:i + 3]) for i in range(0, 18, 3)]
    pa, pb = pal(a), pal(b)
    de = sum(min(sum((x - y) ** 2 for x, y in zip(c, d)) ** 0.5 for d in pb) for c in pa) / 6
    la = list(a.convert("L").resize((24, 36)).getdata())
    lb = list(b.convert("L").resize((24, 36)).getdata())
    ma, mb = sum(la) / len(la), sum(lb) / len(lb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(la, lb))
    va, vb = sum((x - ma) ** 2 for x in la) ** 0.5, sum((y - mb) ** 2 for y in lb) ** 0.5
    return {"palette_de": round(de, 1), "layout_corr": round(cov / (va * vb or 1), 2)}


def selftest():
    good = "<style>@keyframes a{} @media (prefers-reduced-motion:reduce){}</style><p>" + "가" * 300 + " 61%</p><footer>예시</footer>"
    r = check(good, note="예시")
    assert not r["fails"] and r["numbers_to_confirm"] == ["61%"], r
    assert any("GIF" in f for f in check(good + '<img src="a.gif">')["fails"])
    assert any("시안" in f for f in check(good + '<img src="assets/concept.png">')["fails"])
    assert any("script" in f for f in check(good + "<script></script>")["fails"])
    assert not check(good + "<script></script>", allow_js=True)["fails"]
    assert any("글자" in f for f in check("<style>@keyframes a{}</style><p>짧음</p>")["fails"])
    assert any("reduced" in f for f in check("<style>@keyframes a{}</style><p>" + "가" * 300 + "</p>")["fails"])
    assert any("필수" in f for f in check(good, note="없는문구")["fails"])
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("page", nargs="?")
    ap.add_argument("--note")
    ap.add_argument("--allow-js", action="store_true")
    ap.add_argument("--concept")
    ap.add_argument("--shot")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        sys.exit(0)
    r = check(open(a.page, encoding="utf-8", errors="ignore").read(), a.note, a.allow_js)
    if a.concept and a.shot and os.path.exists(a.shot):
        r.update(compare(a.concept, a.shot))
    print(json.dumps(r, ensure_ascii=False, indent=1))
    sys.exit(1 if r["fails"] else 0)
