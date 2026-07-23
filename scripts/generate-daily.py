#!/usr/bin/env python3
"""Daily Game Dev News — 日报生成器 (cron-safe, no hermes_tools dependency)

用法:
  python3 scripts/generate-daily.py --station game --date 2026-07-20
  python3 scripts/generate-daily.py --station game --date 2026-07-20 --data '{...}'

参数:
  --station   game | bio | world  (必填)
  --date      YYYY-MM-DD  (必填)
  --data      JSON string of placeholder values (可选)
  --mermaid   Mermaid chart type: timeline | pie (可选)

该脚本使用标准库 open() 读写文件，不依赖 hermes_tools，可在 cron 环境下安全运行。
"""

import sys, os, re, json
from datetime import datetime, date

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate(station, date_str, data=None, mermaid_type=None):
    """Generate daily HTML from template with given data dict."""
    
    template_path = os.path.join(PROJECT, station, 'template.html')
    if not os.path.exists(template_path):
        print(f'ERROR: Template not found: {template_path}')
        return None
    
    with open(template_path, 'r') as f:
        html = f.read()
    
    # Date formatting
    d = datetime.strptime(date_str, '%Y-%m-%d')
    weekdays = ['星期日','星期一','星期二','星期三','星期四','星期五','星期六']
    date_cn = f"{d.year}年{d.month}月{d.day}日 {weekdays[d.weekday()]}"
    start = date(2026, 7, 1)
    issue_num = (d.date() - start).days + 1
    
    defaults = {
        '[DATE]': date_str,
        '[DATE_CN]': date_cn,
        '[ISSUE_NUM]': str(issue_num),
    }
    
    # Station-specific default images
    if station == 'game':
        defaults['[TOP_IMG]'] = '初音未来-盯着你.avif'
        defaults['[DEV_IMG]'] = '初音未来-贪吃.avif'
        defaults['[GAME_IMG]'] = '雷霆表情包-震惊香蕉.jpg'
        defaults['[AI_IMG]'] = '爱因斯坦-牢大.jpg'
    elif station == 'bio':
        defaults['[TOP_IMG]'] = '初音未来-可爱.avif'
        defaults['[DEV_IMG]'] = '初音未来-可爱.avif'
        defaults['[GAME_IMG]'] = '初音未来-晚安.avif'
        defaults['[AI_IMG]'] = '爱因斯坦-牢大.jpg'
    elif station == 'world':
        defaults['[TOP_IMG]'] = '初音未来-恐惧.avif'
        defaults['[DEV_IMG]'] = '爱因斯坦-牢大.jpg'
        defaults['[GAME_IMG]'] = '初音未来-恐惧.avif'
        defaults['[AI_IMG]'] = '爱因斯坦-牢大.jpg'
    
    if data:
        defaults.update(data)
    
    # Apply all replacements
    for k, v in defaults.items():
        html = html.replace(k, v)
    
    # Fix image paths for daily/ subdirectory
    # template paths: ../assets/images/...  -> daily paths: ../../assets/images/...
    html = html.replace('src="../assets/', 'src="../../assets/')
    
    # Optional Mermaid injection (after headline, before first section)
    if mermaid_type == 'timeline':
        mermaid_block = '  <div class="mermaid-wrapper">\n    <div class="mermaid">\n      timeline\n        title 本周要闻\n    </div>\n  </div>\n  <hr class="section-divider">\n'
        html = html.replace('  <!-- Section: ', mermaid_block + '\n  <!-- Section: ')
    elif mermaid_type == 'pie':
        mermaid_block = '  <div class="mermaid-wrapper">\n    <div class="mermaid">\n      pie title 今日三大领域热度分布\n        "\u6e38\u620f\u5f00\u53d1" : 35\n        "\u6e38\u620f\u5708" : 25\n        "AI\u5708" : 40\n    </div>\n  </div>\n  <hr class="section-divider">\n'
        html = html.replace('  <!-- Section: ', mermaid_block + '\n  <!-- Section: ')
    
    # Verify no leftover placeholders
    leftover = re.findall(r'\[[A-Z_]+\]', html)
    leftover = [x for x in leftover if not (x.startswith('[i') or x.startswith('[0'))]
    
    # Output path
    out_dir = os.path.join(PROJECT, station, 'daily')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'{date_str}.html')
    
    with open(out_path, 'w') as f:
        f.write(html)
    
    file_size = os.path.getsize(out_path)
    print(f'Generated: {out_path} ({file_size} bytes)')
    if leftover:
        print(f'WARNING: {len(leftover)} unset placeholders: {leftover}')
    else:
        print('OK: No leftover placeholders')
    
    return out_path


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate daily HTML report')
    parser.add_argument('--station', required=True, choices=['game', 'bio', 'world'])
    parser.add_argument('--date', required=True, help='YYYY-MM-DD')
    parser.add_argument('--data', type=json.loads, default=None, help='JSON placeholder overrides')
    parser.add_argument('--mermaid', choices=['timeline', 'pie', None], default=None)
    args = parser.parse_args()
    
    generate(args.station, args.date, args.data, args.mermaid)
