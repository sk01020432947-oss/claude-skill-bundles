#!/bin/bash
# 사용법: bash install.sh 1-writing   (묶음 이름: 1-writing 2-presentation 3-paper 4-claude-tips 5-website 6-image-video 7-daycare)
set -e
REPO="https://github.com/sk01020432947-oss/claude-skill-bundles.git"
B="$1"
[ -z "$B" ] && { echo "묶음 이름을 넣어 주세요. 예: bash install.sh 1-writing"; exit 1; }
command -v git >/dev/null || { echo "git이 없습니다. 터미널에서 xcode-select --install 을 먼저 실행하세요."; exit 1; }
TMP=$(mktemp -d)
git clone -q --depth 1 --filter=blob:none --sparse "$REPO" "$TMP"
git -C "$TMP" sparse-checkout set "$B"
[ -d "$TMP/$B" ] || { echo "'$B' 묶음이 없습니다."; exit 1; }
mkdir -p ~/.claude/skills
for d in "$TMP/$B"/*/; do
  n=$(basename "$d")
  if [ -e ~/.claude/skills/"$n" ]; then echo "  건너뜀(이미 있음): $n"
  else cp -R "$d" ~/.claude/skills/"$n" && echo "  설치: $n"; fi
done
rm -rf "$TMP"
echo "완료! Claude Code를 껐다 켜면 새 스킬이 보입니다."
