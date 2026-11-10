---
name: concept-first-web
description: 코드를 쓰기 전에 이미지 모델로 페이지 전체 시안과 움직임 참고를 먼저 만들고, 그것을 HTML/CSS로 다시 지은 뒤 스크립트로 "붙여넣지 않았는지" 검사하는 웹페이지 제작 절차. "시안 먼저", "이미지 먼저 그리고 코드로", "뻔하지 않은 랜딩페이지", "그림 보고 페이지 만들어 줘", "GIF를 코드 애니메이션으로" 요청에 발동. 시안 이미지만 필요하면 codex-image, 기존 사이트 개선은 redesign 계열, 완성 디자인을 쇼케이스 영상으로 뽑는 일은 design-to-motion을 쓴다.
---

# Concept-First Web

순서는 **시안 → 움직임 참고 → 코드로 재건 → 검사**다. 근거와 실측: `~/Desktop/cysjavis/AI동향_검토/GPT이미지2.6_시안먼저_웹페이지/`.

## 1. 시작 전에 정할 것

- **브리프**: 대상, 페이지의 할 일 하나, 섹션 목록, 필수 문구. 사실로 확인된 수치·날짜만 넣는다. 없는 값은 `[확인 필요]`로 둔다.
- **과금**: 기본은 Codex 로그인(`codex-image`)이라 API 요금이 없다. 움직이는 GIF는 OpenAI 이미지 API(`output_format: "gif"`)가 필요하고 종량 과금이므로, 사용자가 명시한 경우에만 쓴다.

## 2. 시안 한 장

`codex-image`로 `1024x1536`, quality high. 프롬프트에 다음을 넣는다.

- "Full-page website design concept, shown flat, no browser frame or device mockup"
- 브리프 전문과 주제의 세계에서 가져온 미술 방향
- 금지: generic SaaS layout, purple gradient, rounded card grid

글자가 뭉개지면 섹션별로 한 장씩 다시 뽑는다. 긴 페이지(8섹션 이상)는 `~/DEV/taste-skill/skills/image-to-code-skill/SKILL.md`의 섹션별 생성 규칙을 따른다.

## 3. 움직임 참고

- **기본(무료)**: 시안을 `--ref`로 넣어 6칸 스토리보드 한 장을 뽑는다. "움직일 요소만 바뀌고 나머지는 고정"을 명시한다.
- **GIF(유료, 명시 요청 시)**: 시안을 참조로 넣고 `frame_count`는 16 이하로 둔다. 총 픽셀 상한이 8,294,400이라 16프레임이면 칸당 720×720까지다. 공식 이미지 수정 엔드포인트는 GIF 출력을 지원하지 않으므로 참조 방식은 플랫폼마다 확인한다. GIF는 움직임 확인용 스케치이고 납품물이 아니다.

## 4. 코드로 재건

코딩 모델(또는 서브에이전트)에 시안과 움직임 참고를 **이미지로 직접 보여 주고** 지시한다.

> Rebuild this design as a real page in HTML and CSS. Recreate every animation in code instead of placing GIFs or the concept image on the page. All text must be real text. Match palette, type character, section order and composition. Everything meant to be read must be visible at rest. Respect prefers-reduced-motion.
>
> The concept supplies the look, and the brief supplies the content. Text in the concept is a layout placeholder, so write the copy a real visitor needs in every section and let sections grow beyond the concept's height. Do not invent logistics such as addresses, parking, door times or dates; write [확인 필요] where such a detail belongs. Use word-break: keep-all for Korean.

**내용 규칙은 빼지 않는다.** 실측에서 이 문단 없이 재건한 2회는 시안의 문구만 옮겨 글자 수가 266~267자로 기준 페이지(1,049~1,181자)의 4분의 1이 됐고, 넣은 2회는 1,775~1,870자가 됐다.

허용되는 이미지는 글자를 뺀 **재료 이미지**뿐이다(예: 코로나 배경을 따로 생성해 깔고 그 위를 코드로 움직이기). 시안 자체는 붙이지 않는다.

## 5. 검사

```bash
python3 ~/.claude/skills/concept-first-web/scripts/check_page.py index.html --note "필수 문구"
```

실패 항목이 있으면 고친다. 스크린샷을 찍었다면 `--concept concept.png --shot shot.png`로 팔레트 거리(`palette_de`, 낮을수록 가까움)와 배치 상관(`layout_corr`, 높을수록 가까움)을 함께 본다. 수치는 참고값이고 최종 판단은 눈으로 한다.

`numbers_to_confirm`에 나온 수치와 `placeholders`로 세어진 `[확인 필요]`는 **전부 사람이 확인한다.** 이미지 모델은 수치와 가격을 지어낸다.

스크립트가 못 보는 것은 눈으로 본다. 실측 6회에서 나온 결함은 **폰 첫 화면에서 글자와 그림이 겹침**(2회), **제목이 낱말 중간에서 끊김**(1회), **폰 가로 넘침**(1회)이었다. 데스크톱과 폰(390px)을 모두 스크린샷으로 확인한다. 스크롤 연동 애니메이션이 있으면 전체 페이지 캡처가 비어 보이므로 reduced-motion으로 찍는다.

## 6. 보고

시안, 페이지, 나란히 비교 이미지, 검사 결과, 확인이 필요한 수치와 문구, 시안과 달라진 점을 함께 낸다.
