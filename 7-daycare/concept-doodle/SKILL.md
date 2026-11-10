---
name: concept-doodle
description: 'Use when the user wants a single black-ink doodle / stick-figure concept illustration that explains one topic at a glance — 흰 배경·검은 펜 손그림·졸라맨·텍스트 없음 정사각 이미지. Triggers "개념 일러스트", "졸라맨 그림", "화이트보드 낙서", "두들 일러스트", "손그림 아이콘", "/concept-doodle". Not for: HTML 덱(doodle-deck·sketch-deck), 컷만화·말풍선(insta-toon), 컬러·사진풍 이미지(media-gen-image).'
---

# concept-doodle — 주제 하나를 졸라맨 손그림 1장으로

주제를 받아 **텍스트 없는 검은 펜 doodle 1장(1:1)** 을 만든다. 되묻지 않고 끝까지 간다.

## 절차

### 1. 장면 설계 (주제 → 시각 은유)
주제에서 아래 4가지를 정한다. 글자로 설명하지 말고 **그림으로만** 전달되게.
- **핵심 의미 한 줄**: 이 그림을 본 사람이 떠올려야 할 것
- **졸라맨 1~2명**: 동작 + 표정(단순: 웃음/놀람/땀/물음표 눈)
- **상징 사물 2~5개**: 주제를 대표하는 아이콘. 크기 과장·은유 허용(예: 시간 → 거대한 시계 끌기)
- **구도**: 중앙 집중, 넓은 여백

### 2. 프롬프트 조립
아래 템플릿에 1단계 결과를 영어로 채운다. 스타일 블록은 고정.

```
A simple hand-drawn concept illustration of {핵심 의미}.
Scene: {졸라맨 동작·표정}, {상징 사물 2~5개와 배치, 과장·은유}.
Style: black ink doodle, very simple stick figure characters, hand-drawn marker sketch,
thick slightly uneven black outlines, minimal line art, whiteboard illustration,
educational concept drawing, cute and playful, visual metaphor,
pure white background, wide empty margins, centered balanced square composition.
No text, no letters, no words, no numbers, no labels.
No color, no shading, no gradients, no texture, no 3D, no photorealism.
```

### 3. 렌더 (codex image_generation, 1:1)
```
codex exec --sandbox workspace-write --skip-git-repo-check -o <log.md> \
  "Using the image_generation tool, create ONE 1:1 square image. {프롬프트}. Save to <산출경로>/<slug>.png"
```
- `<slug>`는 주제의 영어 ASCII 한 단어(예: 번아웃 → `burnout`). 프롬프트는 한 줄로 펴서 넣고, 경로는 공백이 있을 수 있으니 따옴표로 감싼다. 로그는 PNG 옆에 둔다.
- codex 샌드박스는 **현재 작업 폴더 밖에 못 쓴다**(실측: `~/Documents/...` 지정 시 복사 거부). 렌더 후 항상 `ls -dt ~/.codex/generated_images/*/ | head -1` 세션 폴더의 최신 PNG를 목적지로 `cp`한다.
- codex 불가 시 `media-gen-image`(fal.ai, `aspect_ratio: 1:1`)로 대체. 유료면 그 스킬의 비용 확인을 따른다.

### 4. 검수 → 1회 재생성
이미지를 Read로 직접 본다. 아래 하나라도 걸리면 프롬프트의 해당 금지어를 강화해 **1회만** 재생성:
- 글자·숫자가 들어감 (가장 흔한 실패)
- 색·회색 음영·배경 질감이 있음
- 졸라맨이 아닌 사실적 인물
- 주제가 그림만 보고 읽히지 않음 → 사물을 줄이거나 은유를 더 직설적으로

### 5. 산출
`<산출경로>/<slug>.png` 저장. 사용자에게 **클릭 가능한 링크 + 한 줄(어떤 은유를 썼는지)** 만 보고한다.
사용자가 폴더를 지정하지 않으면 `~/Documents/doodles/`에 둔다.

## 예시 (주제: 복리)
작은 졸라맨이 웃으며 동전 하나를 언덕에서 굴리고, 구르면서 동전이 눈덩이처럼 점점 커져 저 아래에는 졸라맨보다 큰 동전 덩이가 되어 있다. 사물: 동전 3단계 크기, 언덕 선, 작은 움직임 선.

## 흔한 실수
- 사물 6개 이상 → 낙서가 아니라 도표가 된다. 5개에서 끊는다.
- 템플릿의 "No text" 줄을 빼먹고 라벨이 박힌 채 납품.
- 주제를 직역(예: "협업" → 두 사람이 서 있기). 동작으로 보여줄 것(두 사람이 한 퍼즐 조각을 맞춤).
