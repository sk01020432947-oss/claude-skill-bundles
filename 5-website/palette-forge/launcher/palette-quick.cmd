@echo off
rem palette-forge quick mode: instant palette HTML (no LLM), opens in browser
python3 "%USERPROFILE%\.claude\skills\palette-forge\scripts\quick_report.py" "%~1" --open
if errorlevel 1 (
  echo [palette-forge] failed - check Python/Pillow
  pause
)
