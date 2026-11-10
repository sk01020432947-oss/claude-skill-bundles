# -*- coding: utf-8 -*-
"""palette-forge: PPTX theme1.xml 테마 색 패치.
사용: python patch_theme.py deck.pptx dk2=1E1B16 lt2=F2E0C8 accent1=DB6F2E ...
슬롯: dk1 lt1 dk2 lt2 accent1~6 hlink folHlink
"""
import sys, zipfile, shutil, re, tempfile, os

def main():
    src = sys.argv[1]
    slots = dict(kv.split("=") for kv in sys.argv[2:])
    tmp = src + ".tmpcopy"
    shutil.copy(src, tmp)
    zin = zipfile.ZipFile(tmp)
    theme = zin.read("ppt/theme/theme1.xml").decode("utf-8")
    for slot, hexv in slots.items():
        hexv = hexv.lstrip("#").upper()
        theme, n = re.subn(
            rf'(<a:{slot}>)<a:(?:srgbClr|sysClr)[^/]*/>(</a:{slot}>)',
            rf'\g<1><a:srgbClr val="{hexv}"/>\g<2>', theme)
        print(slot, "patched" if n else "NOT FOUND")
    with zipfile.ZipFile(src, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = theme.encode("utf-8") if item.filename == "ppt/theme/theme1.xml" else zin.read(item.filename)
            zout.writestr(item, data)
    zin.close()
    os.remove(tmp)
    print("done:", src)

if __name__ == "__main__":
    main()
