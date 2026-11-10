"""Windows compatibility patches for video-use helpers. Re-run after `git pull` if the # win-patch lines are gone."""
from pathlib import Path

ROOT = Path(__file__).parent

# 1) render.py: ffmpeg subtitles filter needs forward slashes on Windows
p = ROOT / "helpers" / "render.py"
s = p.read_text(encoding="utf-8")
old = 'subs_abs = str(subtitles_path.resolve()).replace(":", r"\\:")'
new = 'subs_abs = subtitles_path.resolve().as_posix().replace(":", r"\\:")  # win-patch'
if "# win-patch" not in s:
    assert old in s, "render.py pattern not found"
    p.write_text(s.replace(old, new, 1), encoding="utf-8")
    print("render.py patched")
else:
    print("render.py already patched")

# 2) timeline_view.py: add Windows font paths
p = ROOT / "helpers" / "timeline_view.py"
s = p.read_text(encoding="utf-8")
old = "FONT_CANDIDATES = [\n"
new = (
    "FONT_CANDIDATES = [\n"
    '    "C:/Windows/Fonts/consola.ttf",  # win-patch\n'
    '    "C:/Windows/Fonts/malgun.ttf",   # win-patch (Korean)\n'
    '    "C:/Windows/Fonts/arial.ttf",    # win-patch\n'
)
if "# win-patch" not in s:
    assert old in s, "timeline_view.py pattern not found"
    p.write_text(s.replace(old, new, 1), encoding="utf-8")
    print("timeline_view.py patched")
else:
    print("timeline_view.py already patched")
