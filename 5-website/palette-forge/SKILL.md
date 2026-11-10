---
name: palette-forge
description: >
  이미지·제품 사진·와디즈 등 커머스 페이지에서 브랜드/제품별 고유 컬러를 추출해
  ① 팔레트 HTML 보고서(변형 4단계·대비율·CMYK·PPTX 활용 분석)와
  ② 테마 색이 패치된 7슬라이드 PPTX 테마 덱을 만드는 스킬.
  사용자가 "팔레트 추출", "컬러 추출해서 정리", "이 이미지 색 뽑아줘", "색 분석해서 PPTX",
  "브랜드 컬러 정리", "/palette-forge"를 요청하거나, 이미지·상품 URL을 주며
  "이것도 (동일하게) 해줘"라고 할 때 발동한다. 단색 픽 하나만 원하는 경우(스포이드)는 대상 아님.
---

# palette-forge — 이미지 → 컬러 시스템

이미지에서 색을 뽑는 **기계 층**은 `scripts/`가, 배경 분리·색 이름·위계 분석 같은
**판단 층**은 Claude가 맡는다. 정본 산출물은 `palette.json` 하나이며,
HTML/PPTX는 그 JSON에서 결정론적으로 생성된다.

## 절차

### 0. 입력 확보
- 로컬 이미지: 그대로 사용.
- URL(와디즈 등): 브라우저로 열어 제품별 이미지 URL 수집 후 `curl`로 스크래치패드에 다운로드.
  와디즈 스토리 이미지는 `fetch('/web/apip/funding/global/projects/{id}/story')`에서 URL 추출,
  `www.wadiz.kr` 호스트가 403이면 `cdn.wadiz.kr`/`cdn3.wadiz.kr`로 바꿔 받는다.
- 붙여넣기 이미지(파일 없음): 정량 추출 불가 → 육안 정밀 샘플링으로 진행하고
  보고서에 "육안 샘플링(±5/채널)"을 명시한다.

### 1. 기계 추출
```bash
python ~/.claude/skills/palette-forge/scripts/extract.py IMAGE --n 8 [--drop-bg] [--dark-only] [--crop x0,y0,x1,y1]
```
- 제품이 밝은 배경 위: `--drop-bg`. 어두운 제품(가죽·딥 컬러): `--dark-only` + 제품 영역 `--crop`.
- **결과를 육안 검증할 것** — 상위 클러스터가 배경·그림자·조명이면 크롭/필터를 바꿔 재추출.
  이미지를 Read로 직접 보고 클러스터가 실제 제품색과 일치하는지 확인한다.
- 제품에 색 값이 인쇄돼 있으면(도록·스펙표) 그 공식값이 실측보다 우선한다.

### 2. 판단 층 (Claude 직접)
- 색마다 **이름**(테라코타·페트롤 네이비 등)과 역할 설명을 붙인다.
- 팔레트 **구조**를 읽는다 — 예: 1+5 구조(어두운 색 하나+밝은 다수), 강조 2색 위계,
  다크 샌드위치(어두운 캔버스+밝은 본문), 2톤 밴드. 구조가 PPTX 설계를 결정한다.
- ink(텍스트용 다크)·paper(본문 배경)·canvas(표지/섹션 배경)를 정한다.
- 대비 경고를 도출한다(흰 글자 가능한 색 vs 먹색 필수인 색).

### 3. palette.json 작성
스키마는 `scripts/build_html.py`·`scripts/build_deck.js` 상단 주석 참조.
`analysis_html`(팔레트 성격·대비 주의·테마 매핑 표·추천 조합)과 `deck.*` 필드를 채운다.
**스탯·차트에 지어낸 수치 금지** — 캠페인 실데이터나 팔레트 자체 속성(명도 등)만.

### 4. 산출
```bash
python  ~/.claude/skills/palette-forge/scripts/build_html.py  palette.json  "<이름>-팔레트.html"
node    ~/.claude/skills/palette-forge/scripts/build_deck.js  palette.json  "<이름>-테마.pptx"
python  ~/.claude/skills/palette-forge/scripts/patch_theme.py "<이름>-테마.pptx" dk2=<ink> lt2=<paper> accent1=.. accent2=.. accent3=.. accent4=.. accent5=.. accent6=..
```
- `build_deck.js`는 `NODE_PATH=~/.claude/skills/palette-forge/scripts/node_modules` 필요(사전 설치됨).
- accent 1~6은 analysis_html의 테마 매핑 표와 동일한 순서로.
- 산출물은 사용자가 지정한 위치, 없으면 `~/Documents`에 저장하고 SendUserFile로 전달.

### 5. QA
```bash
"C:/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf "<덱>.pptx" --outdir .
pdftoppm -jpeg -r 100 "<덱>.pdf" slide
```
슬라이드 전부 Read로 확인 — 넘침·겹침·배경에 묻힌 카드(같은 색 위 같은 색)를 잡는다.
표지 캔버스색과 동일한 팔레트 색이 모티프로 들어가면 배경을 Dark 변형으로 낮춘다.

## 참고
- 검증된 사례 5종(임원경제지·보이차·에코닉월렛·한국전통빛깔·코튼양말)이
  `~/Documents`의 `*-팔레트.html`/`*-테마.pptx`에 있다. 새 팔레트의 분석 문체·구성은 이들과 맞춘다.
- 라이트 모드(LLM 없는 즉석 추출)는 `scripts/quick_report.py` — 우클릭 컨텍스트 메뉴 "빠름"이 이걸 호출한다.
