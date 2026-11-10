---
name: insta-toon
description: 어떤 글이든(설교·묵상·강의·아이디어·기록) 1~4컷 인스타툰(4:5)으로 변환하는 스킬. 말풍선과 한글 대사를 이미지에 함께 굽고(in-image 베이크), 렌더 후 스스로 눈으로 검수해 오탈자·일관성 미달이면 재생성한다. 스타일 앵커 이미지를 주면 그 화풍으로 고정한다. "인스타툰", "네컷 만화", "카드툰", "컷만화로 만들어줘", "/insta-toon" 맥락에서 발동.
---

# insta-toon — 글 한 편을 1~4컷 인스타툰으로

글을 받아 **컷 분할 → 말풍선 설계 → 렌더 → 비전 검수 → 재생성**까지 끝까지 자동으로 돈다.
사용자에게 공정을 되묻지 않는다. 컷 수·화풍·대사는 글에서 판단한다.

## 라우팅 (먼저 판정 — 중복 실행 금지)

| 요청 | 담당 |
|---|---|
| 1~4컷 SNS 카드툰 (인스타·스레드) | **이 스킬** |
| 50컷+ 세로 스크롤 웹툰 에피소드 | `[[webtoon-orchestrator]]` |
| 낡은 종이 손판화 일기 카드 (diary.html 발행) | `[[analog-diary]]` |
| 발표 슬라이드·덱 | deck 계열 스킬 |

## 고정 경로

- 산출: `~/Documents\insta-toon\YYYY-MM-DD-{슬러그}\cut-N.png`
- 슬러그는 주제 영문 소문자 케밥(예: `2026-08-28-good-samaritan`)

## 절차

### 1. 컷 수 판정 (질문 금지)

글의 서사 비트 수로 결정한다. 억지로 늘리지 않는다 — 인스타는 모바일에서 작게 보이므로
컷이 많을수록 가독성이 떨어진다.

| 글의 성격 | 컷 수 |
|---|---|
| 한 장면·한 문장 임팩트, 인용구 | 1컷 |
| 상황 → 전환 (대비 구조) | 2컷 |
| 상황 → 갈등 → 해소 | 3컷 |
| 기승전결이 뚜렷하거나 반전이 있음 | 4컷 |

### 2. 컷 대본 작성 (내부 산출, 파일로 저장하지 않음)

컷마다 다음을 정한다:
- **장면**: 무엇이 보이는가 (인물·표정·행동·배경)
- **대사**: 말풍선에 들어갈 한글. **한 풍선당 12자 이내**로 짧게 끊는다(길수록 렌더가 깨진다).
  한 컷당 말풍선 1~2개. 침묵 컷이면 말풍선 없이 SFX만 두거나 아예 비운다.
- **풍선 종류**: 대사=흰 둥근 풍선+꼬리 / 생각=구름형·꼬리 없음 / 외침=뾰족 폭발형 /
  나레이션=사각 박스.
- **캐릭터 고정 토큰**: 등장인물마다 머리·눈·복장·체형을 영문 명사구로 확정하고
  **모든 컷 프롬프트에 동일하게** 넣는다. 누락하면 컷마다 다른 사람이 그려진다.

### 3. 화풍 결정

- 사용자가 **스타일 앵커 이미지**를 줬으면 그 이미지를 `-i`로 넘겨 화풍을 고정한다(권장 경로).
  앵커가 있으면 "많이 본 AI 그림" 느낌이 사라진다 — 이 스킬의 핵심 지렛대.
- 앵커가 없으면 글의 톤으로 판단해 아래 중 선택하고, 선택한 화풍을 **전 컷에 동일 주입**한다.

| 톤 | 화풍 프롬프트 |
|---|---|
| 따뜻함·묵상·간증 | Soft watercolor illustration with gentle warm palette, light pencil underdrawing, tender picture-book atmosphere |
| 일상·공감·유머 | Clean modern webtoon style: crisp expressive ink lines, flat bright colors, lively simple faces, minimal background |
| 손그림 감성 | Hand-drawn analog sketch: slightly crooked wobbling lines, colored-pencil texture on cream paper, charmingly clumsy and warm |
| 진지함·교훈 | Muted editorial illustration: limited desaturated palette, clean shapes, restrained composition, quiet dignity |

### 4. 렌더 (codex-image — 컷당 1회 호출, 동시 5개 이하)

컷마다 아래를 실행한다. `-i`는 스타일 앵커가 있을 때만.

```
codex exec --sandbox workspace-write --skip-git-repo-check [-i <앵커.jpg>] -o <log.md> \
  "Using the image_generation tool, create ONE 4:5 portrait image.
   {화풍 프롬프트}. {캐릭터 고정 토큰}. {컷 장면 묘사}.
   {말풍선 지시 — 아래 규약}.
   negative: no watermark, no English text, no gibberish text, no misspelled text.
   Save to <산출경로>/cut-N.png"
```

**말풍선 in-image 베이크 규약** (오버레이·후작업 절대 금지 — 텍스트는 그림과 함께 그려진다):
- `"no text"` 부정 프롬프트를 쓰지 않는다. 부정은 위의 negative 줄만 쓴다.
- 한글 대사는 **따옴표로 원문 그대로** 명시하고 통합 레터링을 요구한다:
  > a white rounded speech bubble with a tail pointing to {화자}, placed at {위치},
  > containing the EXACT Korean hangul text "그래도 괜찮아" hand-lettered in the same
  > ink as the artwork (not a flat typeset overlay), perfectly legible and correctly spelled
- 인스타 UI는 작으므로 **글씨를 크게**: `text rendered large and bold for small mobile viewing`.
- 말풍선은 얼굴·핵심 작화를 가리지 않는 여백에 둔다.

codex 내부 sandbox exec가 `CreateProcessAsUserW` 오류를 뱉어도 이미지 생성 자체는 끝나 있으므로
로그 오류는 무시한다. 다만 **목적지 복사는 대체로 실패한다** — 결과는 `~/.codex/generated_images/`
아래 세션 폴더에만 남는다(실측 2026-08-28: 8컷 중 6컷이 복사 실패).

**병렬 렌더 시 매핑 규약**: codex 출력에서 경로를 파싱하는 방식은 세션마다 형식이 달라 자주
빈 문자열이 된다. 렌더를 다 돌린 뒤 `ls -dt ~/.codex/generated_images/*/ | head -N`으로 세션 폴더를
**최신순으로 뽑아 실행 순서와 역순 매칭**한 다음 `cut-N.png`로 복사하는 편이 확실하다. 복사 후
`ls`로 컷 수를 세어 누락을 확인한다.

### 5. 비전 검수 → 재생성 루프 (핵심 — 건너뛰지 않는다)

렌더된 PNG를 **Read 도구로 직접 열어 눈으로 확인**한다. 다음 중 하나라도 걸리면 재생성:

| 항목 | 불합격 조건 |
|---|---|
| 한글 텍스트 | 오탈자·깨진 글자·영문 혼입·판독 불가 |
| 캐릭터 일관성 | 컷 간 인물 외형이 다름 (머리·복장·나이대) |
| 말풍선 | 얼굴/핵심 작화를 가림, 꼬리가 엉뚱한 인물을 가리킴 |
| 화풍 | 컷마다 화풍이 튐 |
| 기술 | 0바이트·손상·비율 어긋남 |

재생성 시 **원인에 맞춰 프롬프트만 보강**한다 — 한글 깨짐이면 대사를 더 짧게 끊고 따옴표·굵게·
고대비를 강조, 외형 이탈이면 고정 토큰을 앞으로 당겨 반복, 가림이면 풍선 위치를 명시.
같은 프롬프트로 그냥 다시 돌리지 않는다. **컷당 최대 3회**까지 재시도하고, 3회로도 한글이
안 잡히면 그 컷은 대사를 더 줄이거나 무대사 컷으로 전환한다.

### 6. 전달

- 산출 폴더 경로와 함께 컷들을 사용자에게 보여 준다(SendUserFile).
- **Threads/인스타 발행은 자동으로 하지 않는다.** 발행을 원하면 사용자 확인 후
  `[[moai-threads-poster:threads-post]]`로 넘긴다.

## 자가 점검

작업 종료 전 확인:
- [ ] 컷 수가 글의 비트 수와 맞는가 (억지로 4컷 채우지 않았는가)
- [ ] 모든 컷에 동일한 캐릭터 고정 토큰·화풍이 들어갔는가
- [ ] 모든 PNG를 Read로 실제로 열어 봤는가 (검수 생략은 실패로 간주)
- [ ] 한글 대사가 전부 정확히 읽히는가
