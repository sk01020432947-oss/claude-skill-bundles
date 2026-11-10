---
name: shorts-series
description: "Shorts를 한 편씩이 아니라 '시리즈'로 만들고, 시리즈마다 SERIES.md(형식·단계·검사·피드백·발행규칙)와 편별 수정 장부를 두어 '최근 3–4편 무수정이면 자동 발행 후보'를 기계로 판정하는 스킬. 렌더는 HyperFrames/Remotion, 구간 자르기는 recording-to-series, 피드백 문장은 slop-feedback-ledger에 맡긴다. 실제 업로드는 하지 않는다. 트리거: 쇼츠 시리즈 만들어, 시리즈를 스킬로, 쇼츠 자동화, 무수정 몇 편, 자동 발행 후보, shorts series."
---

# Shorts 시리즈 = 스킬

출처: 커리어해커 알렉스 「숏폼 자동화 — 일주일에 Shorts 약 60개」(2026-10-27, https://www.youtube.com/watch?v=0me1yQSI4uM).
핵심: 시리즈마다 같은 지시 → 같은 결과. 피드백으로 깎다가 내가 고칠 게 없어지면 자동화한다(영상 시점엔 아직 계획).

## 시리즈 폴더
정본 위치: `~/Desktop/cysjavis/유튜브_채널/쇼츠시리즈/<시리즈명>/`

```bash
G=~/.claude/skills/shorts-series/scripts/series_gate.py
python3 $G init   "<폴더>" --name 설교한줄키네틱 --need 3
python3 $G log    "<폴더>" 2026-11-02_롬8장 --edits 2 --note "자막 0.3초 늦음"
python3 $G status "<폴더>"
```

## 한 편 만드는 순서
1. `SERIES.md`를 먼저 읽는다. 형식·검사 기준·피드백 장부를 그대로 따른다.
2. 원재료(자막·원문·발표문)에 없는 사실·숫자는 쓰지 않는다. 통계는 출처 있는 값만, 없으면 "예시".
3. 롱폼 → 쇼츠 구간은 `recording-to-series`로 고르고 시각 검증까지 한다.
4. 화면은 HyperFrames(`hyperframes` 플러그인) 또는 Remotion으로 렌더, 콩트는 Blender.
5. 사용자가 고친 내용은 `slop-feedback-ledger` 형식 한 줄로 SERIES.md 4절에 쌓고, 고친 횟수를 `log --edits N`으로 기록한다.
6. `status`가 "자동 발행 후보"여도 업로드·발행은 하지 않는다. 사용자에게 후보라고만 알린다.

## 금지
- 실제 업로드·예약 발행(외부 발행은 오너 승인 사항)
- AI 실험실 시리즈에서 AI 답을 미리 지어내기
- 콩트에 실제 회사·제품·인물 이름
