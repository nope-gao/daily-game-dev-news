#!/usr/bin/env python3
"""Ad-hoc verification: check daily HTML output for correctness."""
import re, sys

html_path = '/Users/jason-gao/个人其他项目/daily-game-dev-news/game/daily/2026-07-07.html'
with open(html_path) as f:
    html = f.read()

errors = []

# 1. No leftover template placeholders
leftover = re.findall(r'\[[A-Z_]+\]', html)
if leftover:
    errors.append(f'{len(leftover)} unset placeholders: {leftover}')

# 2. All required sections present
checks = {
    'DOCTYPE': '<!DOCTYPE html>' in html,
    'Title date': '2026-07-07' in html,
    'Header avatar': '初音未来-可爱头像.jpg' in html,
    'Edition date': '2026年7月7日 星期二' in html,
    'Issue num': '第 7 期' in html,
    'Keywords section': 'class="keywords"' in html,
    'Headline section': 'class="headline"' in html,
    'Game Dev section': '游戏开发动态' in html,
    'Gaming section': '游戏圈新闻' in html,
    'AI section': 'AI 圈发展' in html,
    'Sources section': '信息来源' in html,
    'Footer GIF': '大黄蜂-点头.gif' in html,
    'Back link': 'index.html' in html,
    '3 news-item blocks': 'news-item' in html,
    'Speed grids (2)': 'speed-grid' in html and html.count('speed-grid') == 2,
    'Dev speed items exist': 'DEV_SPEED' not in html,
    'Game speed items exist': 'GAME_SPEED' not in html,
    'AI speed items exist': 'AI_SPEED' not in html,
}

for name, ok in checks.items():
    if not ok:
        errors.append(f'Missing/failed: {name}')

# 3. Image paths for daily/ subdirectory (must use ../../assets/)
img_refs = re.findall(r'src="([^"]+\.(?:jpg|avif|gif|png))"', html)
if not img_refs:
    errors.append('No images found')
else:
    bad_paths = [p for p in img_refs if not p.startswith('../../assets/')]
    if bad_paths:
        errors.append(f'Image paths not using ../../assets/: {bad_paths}')

# 4. CSS link
if '../assets/style.css' not in html:
    errors.append('CSS link missing/wrong')

# 5. Three section tag classes
for tag in ['tag-dev', 'tag-game', 'tag-ai']:
    if tag not in html:
        errors.append(f'Missing section tag: {tag}')

# Report
if errors:
    for e in errors:
        print(f'FAIL: {e}')
    sys.exit(1)
else:
    print(f'PASS: All {len(checks)} checks OK')
    print(f'  File: {html_path}')
    print(f'  Size: {len(html.encode("utf-8"))} bytes')
    print(f'  Images: {len(img_refs)} ({", ".join(img_refs)})')
    print(f'  Lines: {html.count(chr(10))}')
    sys.exit(0)
