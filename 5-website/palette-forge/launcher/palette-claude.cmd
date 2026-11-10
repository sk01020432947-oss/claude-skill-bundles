@echo off
rem palette-forge precise mode: interactive Claude session running the skill
rem Permission approvals follow your normal Claude Code settings.
title palette-forge (Claude)
cd /d "%USERPROFILE%\Documents"
"~\.local\bin\claude.exe" "Use the palette-forge skill: extract and analyze the color palette of this image (respond in Korean). Save the HTML report and theme PPTX to Documents, then open the HTML. Image: %~1"
