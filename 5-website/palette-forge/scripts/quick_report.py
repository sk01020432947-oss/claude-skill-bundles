# -*- coding: utf-8 -*-
"""palette-forge 라이트 모드: LLM 없이 이미지 → 즉석 팔레트 HTML.
사용: python quick_report.py IMAGE [--n 8] [--open]
산출: <이미지폴더>/<이름>-palette.html
판단 층(배경 분리·색 이름·위계 분석) 없이 기계 추출만 — 정밀 분석은 Claude 스킬 모드 사용.
"""
import sys, os, json, colorsys, argparse, base64, io, subprocess
from pathlib import Path
from PIL import Image

def hx2rgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
def rgb2hx(r, g, b): return f"#{round(r):02X}{round(g):02X}{round(b):02X}"
def darker(h, f):
    r, g, b = hx2rgb(h); return rgb2hx(r*(1-f), g*(1-f), b*(1-f))
def tint(h, f):
    r, g, b = hx2rgb(h); return rgb2hx(r+(255-r)*f, g+(255-g)*f, b+(255-b)*f)
def lum(h):
    def ch(c):
        c /= 255
        return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    r, g, b = hx2rgb(h)
    return 0.2126*ch(r)+0.7152*ch(g)+0.0722*ch(b)
def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return round((la+0.05)/(lb+0.05), 2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--open", action="store_true")
    a = ap.parse_args()
    src = Path(a.image)

    im = Image.open(src).convert("RGB")
    small = im.copy(); small.thumbnail((280, 280))
    # 배경 제거 없이 전체 + 배경 제거 두 벌 추출
    def clusters(drop_bg):
        px = []
        for p in small.getdata():
            _, l, s = colorsys.rgb_to_hls(p[0]/255, p[1]/255, p[2]/255)
            if drop_bg and l > 0.72 and s < 0.45: continue
            px.append(p)
        if len(px) < 50: return []
        tmp = Image.new("RGB", (len(px), 1)); tmp.putdata(px)
        q = tmp.quantize(colors=a.n, method=Image.MEDIANCUT)
        pal = q.getpalette()[:a.n*3]
        cs = sorted(q.getcolors(), reverse=True)
        tot = sum(c for c, _ in cs)
        return [(f"#{pal[i*3]:02X}{pal[i*3+1]:02X}{pal[i*3+2]:02X}", round(c/tot*100, 1)) for c, i in cs]

    full, nobg = clusters(False), clusters(True)

    thumb = im.copy(); thumb.thumbnail((640, 480))
    buf = io.BytesIO(); thumb.save(buf, "JPEG", quality=75)
    b64 = base64.b64encode(buf.getvalue()).decode()

    def row(hexc, share):
        d, li, pa = darker(hexc, 0.25), tint(hexc, 0.35), tint(hexc, 0.78)
        tcol = "#fff" if contrast(hexc, "#FFFFFF") >= contrast(hexc, "#26262A") else "#26262A"
        return f'''<div class="row">
<div class="sw" style="background:{hexc};color:{tcol}" onclick="cp('{hexc}')">{hexc}<small>{share}%</small></div>
<div class="var" style="background:{d}" onclick="cp('{d}')">{d}</div>
<div class="var" style="background:{li}" onclick="cp('{li}')">{li}</div>
<div class="var" style="background:{pa}" onclick="cp('{pa}')">{pa}</div>
<span class="c">흰글자 {contrast(hexc,"#FFFFFF")}:1 · 먹글자 {contrast(hexc,"#26262A")}:1</span></div>'''

    sec = lambda title, cl: f'<h2>{title}</h2>' + "".join(row(h, s) for h, s in cl)
    html = f'''<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{src.name} 팔레트</title>
<style>
* {{box-sizing:border-box;margin:0}} body {{font-family:'Pretendard','Malgun Gothic',sans-serif;background:#F7F5F2;color:#26262A;padding:36px 20px}}
.wrap {{max-width:820px;margin:0 auto}} h1 {{font-size:22px;margin-bottom:4px}} .sub {{color:#8b8680;font-size:13px;margin-bottom:18px}}
img.src {{max-width:100%;border-radius:10px;margin-bottom:22px;box-shadow:0 2px 10px rgba(0,0,0,.12)}}
h2 {{font-size:15px;margin:20px 0 10px}}
.row {{display:flex;gap:6px;align-items:center;margin-bottom:8px}}
.sw {{flex:0 0 190px;height:52px;border-radius:8px;display:flex;align-items:center;justify-content:center;gap:8px;font-weight:700;font-size:13px;cursor:pointer;border:1px solid rgba(0,0,0,.06)}}
.sw small {{font-weight:400;opacity:.8;font-size:11px}}
.var {{flex:0 0 84px;height:52px;border-radius:8px;display:flex;align-items:flex-end;padding:4px 6px;font-size:9.5px;color:rgba(0,0,0,.6);cursor:pointer;border:1px solid rgba(0,0,0,.05)}}
.c {{font-size:11px;color:#8b8680;margin-left:8px}}
.note {{background:#fff;border-radius:10px;padding:14px 16px;font-size:12.5px;color:#8b8680;margin-top:24px;line-height:1.7}}
#toast {{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#26262A;color:#fff;padding:8px 18px;border-radius:20px;font-size:13px;opacity:0;transition:opacity .25s;pointer-events:none}}
</style></head><body><div class="wrap">
<h1>{src.name} — 즉석 팔레트</h1>
<p class="sub">palette-forge 라이트 모드 (기계 추출) · 각 행: 대표색+점유율 → Dark → Light → Pale · 클릭 시 HEX 복사</p>
<img class="src" src="data:image/jpeg;base64,{b64}">
{sec("전체 이미지 기준", full)}
{sec("배경 제거 기준 (밝고 채도 낮은 픽셀 제외)", nobg)}
<div class="note">라이트 모드는 배경·그림자 분리, 색 이름, 위계 분석을 하지 않습니다.
제품별 정밀 팔레트 + PPTX 테마가 필요하면 우클릭 메뉴의 <b>정밀 (Claude)</b> 또는 Claude Code에서 "팔레트 추출"을 사용하세요.</div>
</div><div id="toast">복사됨</div>
<script>function cp(h) {{navigator.clipboard.writeText(h).then(()=>{{const t=document.getElementById('toast');t.textContent=h+' 복사됨';t.style.opacity=1;clearTimeout(window._tt);window._tt=setTimeout(()=>t.style.opacity=0,1200)}})}}</script>
</body></html>'''

    out = src.with_name(src.stem + "-palette.html")
    out.write_text(html, encoding="utf-8")
    print("written:", out)
    if a.open:
        os.startfile(str(out))

if __name__ == "__main__":
    main()
