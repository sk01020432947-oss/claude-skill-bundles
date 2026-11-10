# 자립형 패키지 안내 — grill-me

원본: `~/.cys/pack/skills/grill-me` (CYSJavis Pack 0.14.18) · 계정 스킬 사본 `~/.claude/skills/grill-me`

계정 스킬로 등록되면 클라우드 세션은 이 폴더 하나만 받는다. grill-me 는 문서만으로는 동작하지
않고 **결정론 게이트 본체와 훅**에 의존하므로 다음을 처리했다.

1. 게이트 본체 `bin/grill_gate.py` 와 그것이 같은 폴더에서 호출하는 복잡도 라우터
   `bin/javis_route.py` 를 팩에서 이 폴더 안으로 복사했다(둘 다 표준 라이브러리만 사용 —
   외부 의존성 0). 라우터가 빠지면 복잡도 판정이 `router:no-request(default-20)` 로 고정돼
   `--request` 를 줘도 30 승격이 일어나지 않으므로 반드시 함께 있어야 한다.
   라우터는 다시 같은 폴더의 `bin/route_triggers.json`(트리거 사전)을 읽는다 — 이것까지
   있어야 복잡도 slow/deliberate 판정이 산다. 셋이 한 세트다.
2. 강제 훅 4종과 공용 `_lib.sh` 를 `hooks/` 에 동봉했다.
   `grill-arm.sh`(PreToolUse·자동 무장) · `grill-gate.sh`(PreToolUse·구현 차단) ·
   `grill-count.sh`(질문 카운트) · `grill-stop.sh`(Stop·턴 종료 차단)
3. SKILL.md 의 팩 절대경로 `${CYS_PACK_DIR:-$HOME/.cys/pack}/bin/grill_gate.py` 2곳을
   `"$GRILL"` 로 치환하고, 스킬 폴더 → 팩 순으로 떨어지는 경로 해소 블록을 앞에 넣었다.
   (팩이 설치된 맥에서는 3순위 폴백이 원래 경로를 그대로 집는다 — 기존 동작 불변)

원본은 수정하지 않았다. 이 패키지 사본에서만 치환했다.

## 알아둘 한계 — 훅 없이는 "권고"다
grill-me 의 최소 깊이(20/30 질문)는 **훅이 등록돼 있을 때만 강제**된다. 훅을 등록하지 않으면
SKILL.md 는 읽히지만 게이트가 차단하지 않으므로 사실상 프롬프트 권고로 떨어진다.
등록 방법은 `INSTALL.md` 를 보라.

또한 게이트 마커는 `CYS_SURFACE_ID` 로 노드별 격리된다. 그 환경변수가 없는 환경(일반 단독
세션·클라우드)에서는 `begin` 이 **fail-open**(마커 미생성)으로 떨어진다 — 설계된 동작이며
크래시가 아니다. 단독 환경에서 강제하려면 `GRILL_MARKER` 로 마커 경로를 직접 지정하라.
