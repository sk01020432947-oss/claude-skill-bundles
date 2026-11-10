---
name: remotion-kr
description: '공식 Remotion 스킬(remotion-best-practices 등 12종)을 보완하는 한국어 로컬 보강. 한국어 예제 갤러리 44개 지도·Pretendard 고정·"참고 코드 + :: 정확 명령" 요청 틀, 그리고 공식 스킬에 없는 차트·텍스트 애니메이션·프레임 추출·디코딩 확인 규칙. 리모션 장면을 새로 짜거나 한글 자막·차트·광고 쇼츠를 만들 때 공식 스킬과 함께 읽는다.'
metadata:
  tags: remotion, korean, gallery, charts, text-animation
---

# remotion-kr — 공식 스킬 보강

공식 스킬이 기본이다(`remotion-best-practices`가 라우터, 업데이트는 `remotion-upgrade`). 이 스킬은 `remotion-upgrade`가 건드리지 않도록 따로 둔 로컬 파일이다.

- [rules/kr-gallery-command.md](rules/kr-gallery-command.md) — 한국어 예제 갤러리 44개 지도, Root.tsx·font.ts(Pretendard), `::` 요청 틀, 라이선스 메모. **새 장면은 여기서 가장 가까운 예제부터.**
- [rules/charts.md](rules/charts.md) — 차트·데이터 시각화 패턴
- [rules/text-animations.md](rules/text-animations.md) — 타이포그래피·텍스트 애니메이션
- [rules/extract-frames.md](rules/extract-frames.md) — 영상에서 특정 시점 프레임 추출(Mediabunny)
- [rules/can-decode.md](rules/can-decode.md) — 브라우저 디코딩 가능 여부 확인(Mediabunny)

출처: 옛 `remotion` 스킬 v1.0.1(2026-01)에서 옮김(2026-10-09). 공식 스킬에 같은 주제가 생기면 그쪽을 따르고 여기서 지운다.
