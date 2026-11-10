#!/usr/bin/env python3
"""토큰 다이어트 린트: 지침 파일(SKILL.md·CLAUDE.md·AGENTS.md)에서 토큰을 태우는 문구를 찾는다.
근거: 강수진, 티타임즈 2026-09-29/30 영상 2편. 사용: lint.py <파일|폴더> [...]  /  lint.py --selftest"""
import re, sys, unicodedata
from pathlib import Path

# '매번·항상' 같은 상시어 + 읽기/검토 동사 → 매 턴 파일·스킬을 다시 읽게 만든다
ALWAYS = re.compile(r"(매번|항상|언제나|모든\s*경우|every\s*time|\balways\b|ALWAYS)")
READ = re.compile(r"(읽|검토|확인|참고|불러|로드|read|load|check|review)", re.I)
# 과잉 작업을 부르는 표현 → 분량·검증 범위를 숫자로 바꿀 후보
OVERWORK = re.compile(r"(단계별로|길게\s*생각|자세히\s*설명|step[- ]by[- ]step|여러\s*대안|반복\s*검토|철저히|빠짐없이\s*모두|think\s+(hard|long))", re.I)
# 스킬 description의 부정 트리거(쓰지 않을 때) 표지
NEGATIVE = re.compile(r"(아니|말고|쓰지\s*않|사용하지\s*않|제외|다르다|목적이\s*다|대신|not\b|don't|NOT|instead|맡는다|맡고|발동\s*금지|→\s*[a-z]|\buse\s+[a-z]+-|[a-z]+-[a-z0-9-]+[^.]{0,40}?(영역|사용|달리|쓴다|다룬다면|담당))")
STOP = re.compile(r"(종료\s*조건|완료\s*조건|멈춘다|멈춤|중단|끝낸다|Done when|stop when|완료\s*기준)", re.I)
PRIORITY = re.compile(r"(P0|우선순위|priority|충돌\s*시|상충\s*시)", re.I)


def frontmatter_desc(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    d = re.search(r"^description:\s*(.*?)(?=^\w[\w-]*:|\Z)", m.group(1), re.S | re.M)
    return re.sub(r"\s+", " ", d.group(1)).strip(" |>\"'") if d else None


def lint_text(name, text):
    out = []
    for i, raw in enumerate(text.splitlines(), 1):
        if raw.lstrip().startswith("|"):  # 표는 대개 나쁜 예 모음이라 건너뜀
            continue
        line = re.sub(r"'[^']*'|\"[^\"]*\"|‘[^’]*’|“[^”]*”|「[^」]*」", "", raw)  # 인용된 예시는 빼고 검사
        if ALWAYS.search(line) and READ.search(line):
            out.append(("상시읽기", i, line.strip()[:90]))
        if OVERWORK.search(line):
            out.append(("과잉작업", i, line.strip()[:90]))
    if name.endswith("SKILL.md"):
        desc = frontmatter_desc(text)
        if desc is not None:
            if not NEGATIVE.search(desc):
                out.append(("부정트리거없음", 0, desc[:90]))
            if len(desc) > 600:
                out.append(("설명과다", 0, f"description {len(desc)}자 — 매 세션 상시 로드됨"))
        if len(text.splitlines()) > 60 and not STOP.search(text):
            out.append(("종료조건없음", 0, "60줄 넘는 절차인데 종료·완료 조건 문구가 없음"))
    rules = len(re.findall(r"^\s*(?:\d+\.|[-*])\s", text, re.M))
    if rules >= 15 and not PRIORITY.search(text):
        out.append(("우선순위없음", 0, f"규칙 {rules}개, 충돌 시 우선순위 표기 없음"))
    return out


def files(args):
    for a in args:
        p = Path(a).expanduser()
        if p.is_dir():
            yield from sorted(x for x in p.rglob("*.md")
                              if unicodedata.normalize("NFC", x.name) in ("SKILL.md", "CLAUDE.md", "AGENTS.md"))
        elif p.exists():
            yield p


def main(args):
    total, desc_chars, n_skill, counts = 0, 0, 0, {}
    for f in files(args):
        text = f.read_text(errors="ignore")
        if f.name == "SKILL.md":
            n_skill += 1
            desc_chars += len(frontmatter_desc(text) or "")
        hits = lint_text(f.name, text)
        if not hits:
            continue
        print(f"\n### {f}")
        for kind, ln, s in hits:
            counts[kind] = counts.get(kind, 0) + 1
            print(f"- [{kind}]" + (f" L{ln}" if ln else "") + f" {s}")
        total += len(hits)
    print("\n## 요약")
    print(f"- 스킬 {n_skill}개, description 합계 {desc_chars:,}자 (상시 로드되는 메타데이터)")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"- {k}: {v}건")
    print(f"- 총 {total}건")


def selftest():
    bad = "---\nname: x\ndescription: 문서를 처리한다\n---\n매번 수정하기 전에 architecture.md를 읽으세요\n모든 문제를 단계별로 길게 생각하고 설명해\n"
    kinds = {k for k, _, _ in lint_text("SKILL.md", bad)}
    assert {"상시읽기", "과잉작업", "부정트리거없음"} <= kinds, kinds
    good = "---\nname: y\ndescription: 법률 계약서 PDF를 검토한다. 일반 문서 요약에는 쓰지 않는다.\n---\n스키마 변경 시에만 data.md를 읽는다.\n"
    assert lint_text("SKILL.md", good) == [], lint_text("SKILL.md", good)
    print("selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    selftest() if a == ["--selftest"] else main(a or ["."])
