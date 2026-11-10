# -*- coding: utf-8 -*-
"""palette-forge: palette.json → HTML 팔레트 보고서.
사용: python build_html.py palette.json out.html

palette.json 스키마:
{
  "title": "...", "subtitle": "브랜드/부제(선택)", "source_html": "출처 문단 HTML",
  "paper": "#F7F5F2", "ink": "#26262A",
  "canvas": {"hex": "#...", "label": "캔버스 — ...", "desc": "..."},   // 선택
  "colors": [
    {"name": "테라코타", "sub": "한자/영문(선택)", "desc": "역할 설명",
     "hex": "#DE7852", "origin": "실측/공식값 표기(선택)", "img": "썸네일 경로(선택)"}
  ],
  "analysis_html": "<h3>1. ...</h3><p>...</p>",   // PPTX 활용 분석 — Claude가 작성
  "method": "푸터 추출 방법 설명"
}
"""
import sys, json, base64, io, colorsys
from pathlib import Path

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
def cmyk(h):
    r, g, b = (c/255 for c in hx2rgb(h))
    k = 1-max(r, g, b)
    if k >= 1: return (0, 0, 0, 100)
    return tuple(round(v*100) for v in ((1-r-k)/(1-k), (1-g-k)/(1-k), (1-b-k)/(1-k), k))
def hsl_str(h):
    r, g, b = hx2rgb(h)
    hh, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    return f"{round(hh*360)}° {round(s*100)}% {round(l*100)}%"

def thumb64(path):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((360, 220))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=72)
    return base64.b64encode(buf.getvalue()).decode()

def main():
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])
    PAPER, INK = spec.get("paper", "#F7F5F2"), spec.get("ink", "#26262A")

    cards, overview = [], []
    for c in spec["colors"]:
        main_c = c["hex"].upper()
        dark, light, pale = darker(main_c, 0.25), tint(main_c, 0.35), tint(main_c, 0.78)
        use_white = contrast(main_c, "#FFFFFF") >= contrast(main_c, INK)
        tcol = "#FFFFFF" if use_white else INK
        cw, ci = contrast(main_c, "#FFFFFF"), contrast(main_c, INK)
        r, g, b = hx2rgb(main_c)
        cy, m, y, k = cmyk(main_c)
        bord = "border:1px solid #E5E0D8;" if lum(main_c) > 0.8 else ""
        overview.append(f'<div class="ov" style="background:{main_c};{bord}" onclick="cp(\'{main_c}\')"><span style="color:{tcol}">{c["name"]}</span></div>')
        thumb = f'<div class="thumbwrap"><img src="data:image/jpeg;base64,{thumb64(c["img"])}" alt=""></div>' if c.get("img") else ""
        sub = f' <span class="hanja">{c["sub"]}</span>' if c.get("sub") else ""
        origin = f'<div class="clusters"><span class="ev">{c["origin"]}</span></div>' if c.get("origin") else ""
        cards.append(f"""
<section class="card">{thumb}
  <div class="info">
    <h2>{c["name"]}{sub} <span class="meta">{c.get("desc","")}</span></h2>
    <div class="mainrow">
      <div class="mainswatch" style="background:{main_c};color:{tcol};{bord}" onclick="cp('{main_c}')">{main_c}</div>
      <table class="vals">
        <tr><th>RGB</th><td>{r}, {g}, {b}</td><th>HSL</th><td>{hsl_str(main_c)}</td></tr>
        <tr><th>CMYK</th><td>{cy} {m} {y} {k}</td><th>대비</th><td>흰글자 {cw}:1 · 먹글자 {ci}:1</td></tr>
      </table>
    </div>
    <div class="variants">
      <div style="background:{dark};color:#fff" onclick="cp('{dark}')"><b>Dark</b> {dark}</div>
      <div style="background:{main_c}" onclick="cp('{main_c}')"><b>Main</b> {main_c}</div>
      <div style="background:{light}" onclick="cp('{light}')"><b>Light</b> {light}</div>
      <div style="background:{pale}" onclick="cp('{pale}')"><b>Pale</b> {pale}</div>
    </div>
    {origin}
  </div>
</section>""")

    canvasbar = ""
    if spec.get("canvas"):
        cv = spec["canvas"]
        cvtxt = "#FFFFFF" if contrast(cv["hex"], "#FFFFFF") >= contrast(cv["hex"], INK) else INK
        canvasbar = f'<div class="canvasbar" style="background:{cv["hex"]};color:{cvtxt}" onclick="cp(\'{cv["hex"]}\')"><b>{cv["label"]}</b><code>{cv["hex"]}</code><span>{cv.get("desc","")}</span></div>'

    subtitle = f' <span style="font-size:14px;color:#a39d94;font-weight:400">{spec["subtitle"]}</span>' if spec.get("subtitle") else ""
    analysis = f'<div class="ppt"><h2>PPTX 활용 분석</h2>{spec["analysis_html"]}</div>' if spec.get("analysis_html") else ""
    method = f'<p class="sub" style="margin-top:20px">{spec["method"]}</p>' if spec.get("method") else ""

    html = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{spec["title"]}</title>
<style>
* {{ box-sizing:border-box; margin:0; }}
body {{ font-family:'Pretendard','Malgun Gothic',sans-serif; background:{PAPER}; color:{INK}; padding:40px 20px; }}
.wrap {{ max-width:960px; margin:0 auto; }}
h1 {{ font-size:26px; letter-spacing:-.5px; }}
.sub {{ color:#8b8680; margin:6px 0 4px; font-size:14px; line-height:1.6; }}
.sub a {{ color:inherit; }}
.canvasbar {{ display:flex; align-items:center; gap:12px; border-radius:10px; padding:14px 18px; margin:20px 0 10px; cursor:pointer; }}
.canvasbar b {{ font-size:14px; }} .canvasbar code {{ font-size:13px; opacity:.92; }} .canvasbar span {{ font-size:12px; opacity:.9; }}
.strip {{ display:flex; margin:14px 0 30px; border-radius:10px; overflow:hidden; box-shadow:0 2px 10px rgba(0,0,0,.1); }}
.ov {{ flex:1; height:74px; display:flex; align-items:flex-end; padding:6px; cursor:pointer; }}
.ov span {{ font-size:11px; font-weight:600; }}
.card {{ display:flex; gap:20px; background:#fff; border-radius:12px; padding:18px 20px; margin-bottom:14px; box-shadow:0 1px 6px rgba(0,0,0,.07); align-items:center; }}
.thumbwrap {{ flex:0 0 250px; }} .thumbwrap img {{ width:100%; border-radius:8px; display:block; border:1px solid #ece7de; }}
.info {{ flex:1; min-width:0; }}
h2 {{ font-size:18px; margin-bottom:8px; }}
.hanja {{ font-weight:400; color:#8b8680; font-size:14px; }}
.meta {{ font-size:12.5px; color:#a39d94; font-weight:400; margin-left:6px; }}
.mainrow {{ display:flex; gap:14px; align-items:center; margin-bottom:8px; flex-wrap:wrap; }}
.mainswatch {{ width:124px; height:58px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:700; cursor:pointer; font-size:13.5px; }}
.vals {{ font-size:12.5px; border-collapse:collapse; }}
.vals th {{ text-align:left; color:#a39d94; padding:2px 8px 2px 0; font-weight:600; }}
.vals td {{ padding:2px 16px 2px 0; }}
.variants {{ display:flex; gap:6px; }}
.variants div {{ flex:1; height:42px; border-radius:6px; font-size:10.5px; padding:4px 7px; cursor:pointer; color:rgba(0,0,0,.65); }}
.variants b {{ display:block; font-size:10px; }}
.clusters {{ margin-top:6px; }} .ev {{ font-size:11.5px; color:#a39d94; }}
.ppt {{ background:#fff; border-radius:12px; padding:24px; margin-top:30px; box-shadow:0 1px 6px rgba(0,0,0,.07); }}
.ppt h2 {{ margin-bottom:12px; }} .ppt h3 {{ font-size:15px; margin:18px 0 8px; }}
.ppt p, .ppt li {{ font-size:13.5px; line-height:1.75; }} .ppt ul {{ padding-left:20px; }}
.ppt table {{ border-collapse:collapse; font-size:13px; width:100%; }}
.ppt th, .ppt td {{ border:1px solid #e8e3da; padding:7px 10px; text-align:left; }}
.ppt th {{ background:{PAPER}; }}
code {{ font-family:Consolas,monospace; font-size:12px; }}
.chip {{ display:inline-block; width:12px; height:12px; border-radius:3px; margin-right:5px; vertical-align:-1px; border:1px solid rgba(0,0,0,.12); }}
#toast {{ position:fixed; bottom:24px; left:50%; transform:translateX(-50%); background:{INK}; color:#fff; padding:8px 18px; border-radius:20px; font-size:13px; opacity:0; transition:opacity .25s; pointer-events:none; }}
@media (max-width:720px) {{ .card {{ flex-direction:column; align-items:stretch; }} .thumbwrap {{ flex-basis:auto; }} }}
</style></head><body><div class="wrap">
<h1>{spec["title"]}{subtitle}</h1>
<p class="sub">{spec.get("source_html","")}</p>
{canvasbar}
<div class="strip">{"".join(overview)}</div>
{"".join(cards)}
{analysis}
{method}
</div>
<div id="toast">복사됨</div>
<script>
function cp(h) {{ navigator.clipboard.writeText(h).then(() => {{
  const t = document.getElementById('toast');
  t.textContent = h + ' 복사됨'; t.style.opacity = 1;
  clearTimeout(window._tt); window._tt = setTimeout(() => t.style.opacity = 0, 1200);
}}); }}
</script>
</body></html>"""
    out.write_text(html, encoding="utf-8")
    print(f"written {out} ({len(html)} chars)")

if __name__ == "__main__":
    main()
