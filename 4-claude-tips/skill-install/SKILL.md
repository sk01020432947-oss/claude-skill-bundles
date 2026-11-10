---
name: skill-install
description: 깃허브 URL이나 마켓플레이스로 받은 Claude Code 스킬·플러그인을 설치하기 전에 중복 판정·보안 점검·의존성 확인을 하고, 범위(user/project/local)를 정해 설치한 뒤 작동을 확인한다. "이 스킬 설치해 줘", "깃허브 스킬 깔아 줘", "플러그인 추가해 줘", "/plugin marketplace add", "SKILL.md 복사해서 넣어 줘" 요청에 사용. 스킬을 찾기만 할 때는 skill-scout, 새로 만들 때는 skill-creator, 설치된 스킬 감사·정리는 skill-stocktake·config-gc를 쓴다.
---

# skill-install

출처: 「클로드 코드 스킬 설치 3가지 방법」(쉽게 AI 알려주는 개발자, 2026-09-13)의 세 방법에 점검 단계를 더했다.

## 순서

1. **중복 판정 (먼저, 생략 금지).** 대상의 name·description을 읽고 기존 자산과 대조한다.
   ```bash
   grep -rhiE "^(name|description):.*(키워드1|키워드2)" ~/.claude/skills/*/SKILL.md ~/.claude/plugins/cache/*/*/*/skills/*/SKILL.md 2>/dev/null
   ```
   역할이 겹치는 스킬이 있으면 설치하지 않고 그 스킬 이름과 차이를 보고한다. 사용자가 그래도 원하면 local 범위로만 시험 설치한다.

2. **구조 확인.** 저장소 루트에 `.claude-plugin/marketplace.json`이 있으면 방법 ①, 없고 `skills/<이름>/SKILL.md`만 있으면 방법 ② 또는 ③.

3. **보안 점검.** 받은 폴더를 임시 디렉터리에 clone해서 읽는다(스크래치패드 사용).
   ```bash
   grep -rnE "curl[^|]*\|\s*(ba)?sh|wget .*\|\s*sh|rm -rf|ANTHROPIC_API_KEY|\.env|ssh|base64 -d|eval\(|hooks" <폴더>
   ```
   scripts/·hooks 등록·외부 전송이 있으면 해당 줄을 인용해 보고하고, 설치 여부를 사용자에게 묻는다. 별 수는 안전 근거가 아니다.

4. **의존성.** SKILL.md·README에서 다른 스킬, 바이너리(ffmpeg 등), 환경변수 요구를 찾아 함께 알린다. 의존 스킬이 있으면 같이 가져온다.

5. **범위 결정.** 사용자가 말하지 않았으면 묻는다. 기본 추천: 시험은 local, 프로젝트 전용은 project, 어디서나 쓰는 것만 user.
   | 범위 | 스킬 폴더 | 플러그인 설정 |
   |---|---|---|
   | user | `~/.claude/skills/` | `~/.claude/settings.json` |
   | project | `.claude/skills/` | `.claude/settings.json` (git 공유) |
   | local | `.claude/skills/` + `.gitignore` | `.claude/settings.local.json` |

6. **설치.**
   - ① `/plugin marketplace add owner/repo` → `/plugin install <플러그인>@<marketplace.json의 name>` (셸: `claude plugin install … --scope <범위>`)
   - ② 저장소의 스킬 폴더 **전체**(scripts·references 포함)를 범위 폴더로 복사
   - ③ 단일 파일 스킬만: `SKILL.md` 원문을 `<범위폴더>/<name>/SKILL.md`로 저장. 폴더 이름은 frontmatter `name`과 같게.
   한글 경로가 끼면 셸 글롭 대신 python3으로 처리한다.

7. **확인.** 파일 위치를 링크로 보여 주고, 새 세션에서 `/<name>`이 보이는지와 한 번의 시험 요청을 안내한다. 플러그인은 재시작이 필요하다.

## 보고 형식

판정(설치함/설치 안 함/보류) · 겹친 기존 스킬 · 보안 점검 결과 · 범위와 경로 · 확인 방법, 다섯 줄 이내.
