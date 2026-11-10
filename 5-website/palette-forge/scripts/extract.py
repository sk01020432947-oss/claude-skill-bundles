# -*- coding: utf-8 -*-
"""palette-forge: median-cut 색 추출기.
사용: python extract.py IMAGE [--n 8] [--crop x0,y0,x1,y1(0~1 비율)] [--drop-bg] [--dark-only] [--light-only]
출력: 클러스터 JSON (hex/share/hsl) → stdout
"""
import sys, json, colorsys, argparse
from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--crop", help="x0,y0,x1,y1 (0~1 비율)")
    ap.add_argument("--drop-bg", action="store_true", help="밝고 채도 낮은 배경(스튜디오 흰/크림) 제거")
    ap.add_argument("--dark-only", action="store_true", help="명도 60%% 미만 픽셀만 (어두운 제품 추출)")
    ap.add_argument("--light-only", action="store_true", help="명도 40%% 이상 픽셀만")
    a = ap.parse_args()

    im = Image.open(a.image).convert("RGB")
    if a.crop:
        x0, y0, x1, y1 = map(float, a.crop.split(","))
        w, h = im.size
        im = im.crop((int(w*x0), int(h*y0), int(w*x1), int(h*y1)))
    im = im.resize((280, max(1, int(280 * im.height / im.width))))

    px = []
    for p in im.getdata():
        _, l, s = colorsys.rgb_to_hls(p[0]/255, p[1]/255, p[2]/255)
        if a.drop_bg and l > 0.72 and s < 0.45: continue
        if a.dark_only and l >= 0.60: continue
        if a.light_only and l < 0.40: continue
        px.append(p)
    if len(px) < 50:
        print(json.dumps({"error": "필터 후 픽셀 부족", "left": len(px)})); return

    tmp = Image.new("RGB", (len(px), 1)); tmp.putdata(px)
    q = tmp.quantize(colors=a.n, method=Image.MEDIANCUT)
    pal = q.getpalette()[:a.n*3]
    cs = sorted(q.getcolors(), reverse=True)
    tot = sum(c for c, _ in cs)
    out = []
    for c, i in cs:
        r, g, b = pal[i*3:i*3+3]
        hh, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        out.append({"hex": f"#{r:02X}{g:02X}{b:02X}", "share": round(c/tot*100, 1),
                    "hsl": [round(hh*360), round(s*100), round(l*100)]})
    print(json.dumps({"image": a.image, "clusters": out}, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
