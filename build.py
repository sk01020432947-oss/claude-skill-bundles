# 내 ~/.claude/skills 에서 묶음별로 복사(.git/.venv/node_modules 제외, 개인 경로·이메일 치환)
import os, shutil, sys
SRC = os.path.expanduser('~/.claude/skills')
B = {
 '1-writing': ['adult-vocabulary-writing-coach','frontline-writing-coach','godowon-writing-coach','yuhongjun-writing-coach','my-writing-master-prompt','seeing-writing-lens','technique-transfer','writing-analytical-essay','reading-craft','korean-humanizer','toego-korean','ste-korean','korean-spell-check','korean-character-count'],
 '2-presentation': ['claude-ppt','html-ppt','my-ppt','pptx-design-styles','ppt-maestro','ppt-template-fill','doodle-deck','monoline-deck','stripe-deck','genie-deck','sketch-deck','kbg-infographic','diagram-design','html-diagram','awesome-ai-motion','opus-motion-playbook','hyperframes'],
 '3-paper': ['paper-writing-master','paper-writing-order','paper-critical-review','paper-study','paper-lookup','keris-academic-search','kci-journal-finder','peer-review','scientific-writing','statistical-analysis','hypothesis-generation','reporting-guideline-router','zotero'],
 '4-claude-tips': ['ai-license-3day','find-skills','skill-install','grill-me','think','planner','deep-interview','context-budget','token-diet','agents-md','git-teacher','save','task-orchestrator','work-tool-tailor'],
 '5-website': ['frontend-design','10k-websites','concept-first-web','clone-website','design-taste-frontend','ui-ux-pro-max','uxui-design-system','better-colors','better-typography','palette-forge','favicon-generator','open-graph','website-structure','seo-audit'],
 '6-image-video': ['media-gen','media-gen-image','media-gen-video','media-gen-thumbnail','codex-image','photo-retouch','character-style-prompts','insta-toon','concept-doodle','brand-visual-generator','script-writer','explainer-video','shorts-series','motion-broll','sound-effects','video-use','remotion-best-practices','remotion-kr','manim-video'],
 '7-daycare': ['@daycare-helper','hwpx','read-hwp','k-schoollunch-menu','meeting-agenda','korean-privacy-terms','korean-spell-check','insta-toon','concept-doodle'],
}
SKIP = shutil.ignore_patterns('.git','.venv','venv','node_modules','__pycache__','.DS_Store','*.pyc')
REPL = [('/Users/kbg1023','~'),('sk01020432947@gmail.com','your-email@example.com'),('동기화 계정 `KBG1023`','동기화 계정 (본인 것)')]
TEXT = ('.md','.py','.sh','.json','.js','.txt','.html','.yaml','.yml','.toml','.ts','.css','.cmd')
for b, names in B.items():
    if os.path.exists(b): shutil.rmtree(b)
    for n in names:
        src = os.path.join('extra', n[1:]) if n.startswith('@') else os.path.join(SRC, n)
        dst = os.path.join(b, n.lstrip('@'))
        shutil.copytree(os.path.realpath(src), dst, ignore=SKIP, symlinks=False)
        for r, _, fs in os.walk(dst):
            for f in fs:
                p = os.path.join(r, f)
                if f.endswith(TEXT):
                    try: t = open(p, encoding='utf-8').read()
                    except Exception: continue
                    t2 = t
                    for a, c in REPL: t2 = t2.replace(a, c)
                    if t2 != t: open(p, 'w', encoding='utf-8').write(t2)
    for d in ['2-presentation/awesome-ai-motion/site','2-presentation/html-diagram/compare']:
        if d.startswith(b) and os.path.exists(d): shutil.rmtree(d)  # SKILL.md가 참조하지 않는 데모 폴더
    print(b, len(names))
