// palette-forge: palette.json → 7슬라이드 PPTX 테마 덱
// 사용: node build_deck.js palette.json out.pptx
//
// deck 관련 JSON 필드(모두 선택, colors는 필수):
//   deck: {
//     titleLines: [["첫 줄", null], ["둘째 줄", "#강조색"]],  // null=기본 텍스트색
//     eyebrow: "TITLE EYEBROW", brand: "부제/브랜드 한 줄", credit: "하단 크레딧",
//     canvas: "#섹션·표지 배경색",  // 없으면 colors 중 가장 어두운 색
//     sectionTitle: "섹션 예시 제목", sectionSub: "섹션 예시 부제",
//     stats: [["10","컬러","설명","#색"], ...],           // 최대 4
//     rules: [["태그","#색","설명"], ...],                 // 최대 5
//     chartTitle: "차트 제목", chartSubtitle: "...",
//     chartValues: [..], chartName: "시리즈명"             // 없으면 명도(L%) 자동
//   }
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const [specPath, outPath] = process.argv.slice(2);
const spec = JSON.parse(fs.readFileSync(specPath, "utf-8"));
const strip = h => h.replace("#", "").toUpperCase();

function hx2rgb(h) { return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); }
function rgb2hx(r, g, b) { return [r, g, b].map(v => Math.round(Math.max(0, Math.min(255, v))).toString(16).padStart(2, "0")).join("").toUpperCase(); }
function darker(hex, f) { const [r, g, b] = hx2rgb(hex); return rgb2hx(r * (1 - f), g * (1 - f), b * (1 - f)); }
function tint(hex, f) { const [r, g, b] = hx2rgb(hex); return rgb2hx(r + (255 - r) * f, g + (255 - g) * f, b + (255 - b) * f); }
function lumi(hex) { const [r, g, b] = hx2rgb(hex).map(c => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; }
function hslL(hex) { const [r, g, b] = hx2rgb(hex).map(v => v / 255); return Math.round((Math.max(r, g, b) + Math.min(r, g, b)) / 2 * 100); }

const PAPER = strip(spec.paper || "#F7F5F2"), INK = strip(spec.ink || "#26262A"), WHITE = "FFFFFF", MUTED = "A39D94";
const COLORS = spec.colors.map(c => ({ ...c, hex: strip(c.hex) }));
const deck = spec.deck || {};
const CANVAS = strip(deck.canvas || COLORS.reduce((a, b) => lumi(a.hex) < lumi(b.hex) ? a : b).hex);
const ACCENT = strip(deck.accent || COLORS.filter(c => c.hex !== CANVAS)[0].hex);
const F = "Malgun Gothic";
const needsBorder = hex => lumi(hex) > 0.8;
const txtOn = hex => lumi(hex) > 0.42 ? INK : WHITE;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";

// ---------- S1 표지 ----------
{
  const s = pres.addSlide();
  s.background = { color: CANVAS };
  COLORS.slice(0, 10).forEach((c, i) => {
    const n = Math.min(COLORS.length, 10);
    const x = 7.6 + i * (4.6 / n), y = 1.8 + (i % 2) * 0.5;
    s.addShape("roundRect", {
      x, y, w: 0.6, h: 3.4, rectRadius: 0.3, rotate: 16,
      fill: { color: c.hex },
      line: { color: c.hex === CANVAS ? tint(c.hex, 0.35) : CANVAS, width: c.hex === CANVAS ? 1 : 0 },
      shadow: { type: "outer", color: darker(CANVAS, 0.5), opacity: 0.25, blur: 7, offset: 3, angle: 90 },
    });
  });
  const canvasIsLight = lumi(CANVAS) > 0.42;
  const baseTxt = canvasIsLight ? INK : WHITE;
  if (deck.eyebrow) s.addText(deck.eyebrow, { x: 0.7, y: 1.7, w: 6.5, h: 0.4, fontFace: F, fontSize: 14, color: canvasIsLight ? MUTED : tint(CANVAS, 0.5), charSpacing: 4, margin: 0 });
  const lines = deck.titleLines || [[spec.title, null]];
  s.addText(lines.map((l, i) => ({ text: l[0] + (i < lines.length - 1 ? "\n" : ""), options: { color: l[1] ? strip(l[1]) : baseTxt } })),
    { x: 0.66, y: 2.15, w: 6.8, h: 2.2, fontFace: F, fontSize: 50, bold: true, lineSpacing: 62, margin: 0 });
  if (deck.brand) s.addText(deck.brand, { x: 0.7, y: 4.45, w: 6.8, h: 0.4, fontFace: F, fontSize: 16, color: canvasIsLight ? INK : tint(CANVAS, 0.7), margin: 0 });
  if (deck.credit) s.addText(deck.credit, { x: 0.7, y: 6.6, w: 9, h: 0.35, fontFace: F, fontSize: 11, color: canvasIsLight ? MUTED : tint(CANVAS, 0.45), margin: 0 });
  s.addNotes("표지: 팔레트 캔버스색 배경 + 컬러 스틱 모티프.");
}

// ---------- S2 팔레트 개요 ----------
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  s.addText("팔레트", { x: 0.7, y: 0.45, w: 12, h: 0.7, fontFace: F, fontSize: 30, bold: true, color: INK, margin: 0 });
  if (deck.paletteSubtitle) s.addText(deck.paletteSubtitle, { x: 0.7, y: 1.12, w: 12, h: 0.35, fontFace: F, fontSize: 13, color: MUTED, margin: 0 });
  const n = COLORS.length, cols = n <= 4 ? n : n <= 8 ? 4 : 5;
  const cw = (11.9 - (cols - 1) * 0.14) / cols, rows = Math.ceil(n / cols);
  const ch = rows <= 2 ? 2.5 : 1.7, y0 = 1.7;
  COLORS.forEach((c, i) => {
    const x = 0.7 + (i % cols) * (cw + 0.14), y = y0 + Math.floor(i / cols) * (ch + 0.25);
    s.addShape("roundRect", { x, y, w: cw, h: ch * 0.62, fill: { color: c.hex }, rectRadius: 0.07, line: { color: "E5E0D8", width: needsBorder(c.hex) ? 1 : 0 } });
    s.addText(`#${c.hex}`, { x: x + 0.14, y: y + ch * 0.62 - 0.42, w: cw - 0.28, h: 0.32, fontFace: "Consolas", fontSize: 11.5, bold: true, color: txtOn(c.hex), margin: 0 });
    const [r, g, b] = hx2rgb(c.hex);
    s.addText([
      { text: `${c.name}\n`, options: { fontSize: 13.5, bold: true, color: INK } },
      { text: `RGB ${r} · ${g} · ${b}${c.origin ? "  " + c.origin : ""}`, options: { fontSize: 9.5, color: MUTED } },
    ], { x, y: y + ch * 0.62 + 0.08, w: cw, h: 0.72, fontFace: F, lineSpacing: 15, margin: 0 });
  });
  s.addNotes("각 카드의 hex를 그대로 복사해 사용.");
}

// ---------- S3 변형 시스템 ----------
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  s.addText("변형 시스템 — Dark · Main · Light · Pale", { x: 0.7, y: 0.45, w: 12, h: 0.7, fontFace: F, fontSize: 30, bold: true, color: INK, margin: 0 });
  const n = Math.min(COLORS.length, 8);
  const twoCol = n > 5, rw = twoCol ? 5.95 : 11.9;
  const rh = Math.min(1.5, 5.3 / Math.ceil(n / (twoCol ? 2 : 1)));
  COLORS.slice(0, 8).forEach((c, i) => {
    const x = 0.7 + (twoCol ? (i % 2) * (rw + 0.28) : 0), y = 1.75 + Math.floor(i / (twoCol ? 2 : 1)) * rh;
    s.addText(c.name, { x, y: y + 0.18, w: 1.1, h: 0.6, fontFace: F, fontSize: 11.5, bold: true, color: INK, margin: 0 });
    [["Dark", darker(c.hex, 0.25)], ["Main", c.hex], ["Light", tint(c.hex, 0.35)], ["Pale", tint(c.hex, 0.78)]].forEach(([label, hex], j) => {
      const chipW = (rw - 1.2 - 3 * 0.08) / 4;
      const cx = x + 1.2 + j * (chipW + 0.08);
      s.addShape("roundRect", { x: cx, y, w: chipW, h: rh - 0.55, rectRadius: 0.05, fill: { color: hex }, line: { color: "E5E0D8", width: 0.75 } });
      s.addText(`${label} #${hex}`, { x: cx, y: y + rh - 0.52, w: chipW, h: 0.3, fontFace: F, fontSize: 7.5, align: "center", color: MUTED, margin: 0 });
    });
  });
  s.addNotes("Dark=-25%, Light=+35% 흰색, Pale=+78% 흰색.");
}

// ---------- S4 섹션 구분 예시 ----------
{
  const s = pres.addSlide();
  s.background = { color: CANVAS };
  const canvasIsLight = lumi(CANVAS) > 0.42;
  const baseTxt = canvasIsLight ? INK : WHITE;
  s.addText("01", { x: 0.7, y: 1.3, w: 4, h: 2, fontFace: F, fontSize: 120, bold: true, color: darker(CANVAS, canvasIsLight ? 0.2 : 0.3), margin: 0 });
  s.addText(deck.sectionTitle || "섹션 제목 예시", { x: 0.75, y: 3.6, w: 9, h: 0.9, fontFace: F, fontSize: 44, bold: true, color: baseTxt, margin: 0 });
  if (deck.sectionSub) s.addText(deck.sectionSub, { x: 0.75, y: 4.55, w: 9.5, h: 0.5, fontFace: F, fontSize: 18, color: canvasIsLight ? MUTED : tint(CANVAS, 0.7), margin: 0 });
  COLORS.filter(c => c.hex !== CANVAS).slice(0, 3).forEach((c, j) => {
    s.addShape("roundRect", { x: 10.4 + j * 0.75, y: 1.8 + j * 0.45, w: 0.55, h: 3.1, rectRadius: 0.27, rotate: 16, fill: { color: c.hex } });
  });
  s.addNotes("섹션 구분: 캔버스색 풀블리드 + 컬러 스틱 모티프.");
}

// ---------- S5 스탯 콜아웃 ----------
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  s.addText("본문 레이아웃 예시 — 스탯 콜아웃", { x: 0.7, y: 0.45, w: 12, h: 0.7, fontFace: F, fontSize: 30, bold: true, color: INK, margin: 0 });
  const stats = (deck.stats || [[String(COLORS.length), "색", "팔레트 구성", "#" + ACCENT]]).slice(0, 4);
  const cw = 2.92, y0 = 1.7;
  stats.forEach(([num, unit, label, hexRaw], i) => {
    const hex = strip(hexRaw);
    const x = 0.7 + i * (cw + 0.14);
    s.addShape("roundRect", { x, y: y0, w: cw, h: 2.3, fill: { color: WHITE }, rectRadius: 0.07, shadow: { type: "outer", color: INK, opacity: 0.1, blur: 7, offset: 2, angle: 90 } });
    s.addShape("roundRect", { x: x + 0.26, y: y0 + 0.28, w: 0.4, h: 0.4, rectRadius: 0.2, fill: { color: hex }, line: { color: "E5E0D8", width: needsBorder(hex) ? 1 : 0 } });
    s.addText([
      { text: num, options: { fontSize: 42, bold: true, color: lumi(hex) > 0.75 ? INK : darker(hex, 0.2) } },
      { text: " " + unit, options: { fontSize: 16, color: MUTED } },
    ], { x: x + 0.24, y: y0 + 0.75, w: cw - 0.48, h: 0.9, fontFace: F, margin: 0 });
    s.addText(label, { x: x + 0.26, y: y0 + 1.72, w: cw - 0.52, h: 0.4, fontFace: F, fontSize: 13, color: INK, margin: 0 });
  });
  s.addNotes("스탯 수치는 실데이터만 사용할 것 — 지어내지 않기.");
}

// ---------- S6 차트 ----------
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  s.addText(deck.chartTitle || "차트 예시 — 팔레트 명도", { x: 0.7, y: 0.45, w: 12, h: 0.7, fontFace: F, fontSize: 30, bold: true, color: INK, margin: 0 });
  if (deck.chartSubtitle) s.addText(deck.chartSubtitle, { x: 0.7, y: 1.12, w: 12, h: 0.35, fontFace: F, fontSize: 13, color: MUTED, margin: 0 });
  s.addChart("bar", [{
    name: deck.chartName || "명도(L%)",
    labels: COLORS.map(c => c.name),
    values: deck.chartValues || COLORS.map(c => hslL(c.hex)),
  }], {
    x: 0.7, y: 1.7, w: 11.9, h: 5.0, barDir: "col",
    chartColors: COLORS.map(c => c.hex), varyColorsByPoint: true,
    showLegend: false, showTitle: false,
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: INK, dataLabelFontFace: F, dataLabelFontSize: 11,
    catAxisLabelColor: INK, catAxisLabelFontFace: F, catAxisLabelFontSize: 10.5,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
  });
  s.addNotes("기본값은 각 색의 HSL 명도 — 실데이터가 있으면 deck.chartValues로 교체.");
}

// ---------- S7 사용 가이드 ----------
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  s.addText("사용 가이드", { x: 0.7, y: 0.45, w: 12, h: 0.7, fontFace: F, fontSize: 30, bold: true, color: INK, margin: 0 });
  const rules = (deck.rules || [["캔버스", "#" + CANVAS, "표지·섹션 배경."], ["본문", "#" + PAPER, "본문 배경 + 흰 카드 + 잉크 텍스트."]]).slice(0, 5);
  rules.forEach(([tag, hexRaw, desc], i) => {
    const hex = strip(hexRaw);
    const y = 1.55 + i * 1.06;
    s.addShape("roundRect", { x: 0.7, y: y + 0.08, w: 0.62, h: 0.62, rectRadius: 0.31, fill: { color: hex }, line: { color: "E5E0D8", width: 1 } });
    s.addText(tag, { x: 1.55, y: y + 0.02, w: 3.2, h: 0.4, fontFace: F, fontSize: 16, bold: true, color: INK, margin: 0 });
    s.addText(desc, { x: 1.55, y: y + 0.42, w: 10.9, h: 0.55, fontFace: F, fontSize: 13, color: INK, margin: 0 });
  });
  s.addNotes("팔레트별 사용 원칙 요약.");
}

pres.writeFile({ fileName: outPath }).then(() => console.log("deck written:", outPath));
