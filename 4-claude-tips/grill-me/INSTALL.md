# 설치

## 1. 스킬 등록
이 폴더(`grill-me/`)를 통째로 스킬 디렉터리에 둔다.
- 개인 전역: `~/.claude/skills/grill-me/`
- 프로젝트: `<repo>/.claude/skills/grill-me/`

여기까지만 해도 스킬은 발동한다(문서 기반 권고 모드).

## 2. 강제 게이트 등록 (선택 — 최소 깊이를 실제로 강제하려면 필요)
`~/.claude/settings.json` 의 `hooks` 에 아래를 더한다. `<SKILL>` 은 이 폴더의 절대경로다.

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Skill", "hooks": [{ "type": "command", "command": "sh <SKILL>/hooks/grill-arm.sh" }] },
      { "matcher": "Write|Edit|NotebookEdit", "hooks": [{ "type": "command", "command": "sh <SKILL>/hooks/grill-gate.sh" }] },
      { "matcher": "AskUserQuestion", "hooks": [{ "type": "command", "command": "sh <SKILL>/hooks/grill-count.sh" }] }
    ],
    "Stop": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "sh <SKILL>/hooks/grill-stop.sh" }] }
    ]
  }
}
```

`CYSJavis Pack` 이 이미 설치된 기기라면 이 훅들은 팩이 등록해 두었으므로 **다시 등록하지 마라**
(중복 발화한다). `~/.claude/settings.json` 에 `grill-` 문자열이 이미 있으면 그 경우다.

## 3. 요구사항
- `python3` (표준 라이브러리만 사용 — pip 설치 불요)
- `sh`

## 4. 확인
```sh
python3 <SKILL>/bin/grill_gate.py --help
```
