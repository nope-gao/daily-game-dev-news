#!/bin/bash
# ============================================
# 游戏开发 & AI 圈每日速递 — 部署脚本
# 用法: bash deploy.sh [commit message]
# ============================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$PROJECT_DIR"

echo "==> [1/4] 检查最新日报..."
latest_html=$(ls -t daily/*.html 2>/dev/null | head -1)

if [ -z "$latest_html" ]; then
    echo "    未找到日报文件 (daily/*.html)，跳过"
    exit 0
fi

echo "    最新: $latest_html"

echo "==> [2/4] 自动更新 index.html 存档数据..."

python3 -c "
import os, re, json
from datetime import datetime

daily_dir = 'daily'
index_path = 'index.html'
weekdays = ['星期一','星期二','星期三','星期四','星期五','星期六','星期日']

# 1. 读取 index.html 中已有的 ARCHIVE_DATA
with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

existing = {}
m = re.search(r'var ARCHIVE_DATA\s*=\s*(\[.*?\]);', html, re.DOTALL)
if m:
    try:
        old_data = json.loads(m.group(1))
        for item in old_data:
            existing[item['date']] = item
    except Exception as e:
        print(f'    解析已有存档数据失败: {e}')

# 2. 扫描 daily/ 目录，找出所有日期
new_dates = set()
for f in os.listdir(daily_dir):
    dm = re.match(r'(\d{4}-\d{2}-\d{2})\.html$', f)
    if dm:
        new_dates.add(dm.group(1))

# 3. 合并：保留已有关键词 + 补充新日期
entries = []
for date_str in sorted(new_dates | set(existing.keys()), reverse=True):
    if date_str in existing:
        entries.append(existing[date_str])
    else:
        try:
            d = datetime.strptime(date_str, '%Y-%m-%d')
            weekday = weekdays[d.weekday()]
        except Exception:
            weekday = ''
        # 尝试从HTML提取关键词
        keywords = ''
        filepath = os.path.join(daily_dir, date_str + '.html')
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                    kw_match = re.search(r'<div[^>]*keywords-banner[^>]*>\s*<strong>[^<]*</strong>(.*?)</div>', content, re.DOTALL)
                    if kw_match:
                        raw = re.sub(r'<[^>]+>', '', kw_match.group(1)).strip()
                        keywords = raw
            except Exception:
                pass
        entries.append({
            'date': date_str,
            'weekday': weekday,
            'keywords': keywords
        })

entries.sort(key=lambda x: x['date'], reverse=True)

# 4. 替换 index.html 中的 ARCHIVE_DATA
js_data = json.dumps(entries, ensure_ascii=False, indent=4)
pattern = r'(var ARCHIVE_DATA\s*=\s*)\[.*?\](;)'
replacement = r'\1' + js_data + r'\2'
new_html, count = re.subn(pattern, replacement, html, flags=re.DOTALL)

if count == 0:
    print('    警告: 未找到 ARCHIVE_DATA，index.html 未更新')
else:
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'    已更新 index.html ({len(entries)} 条存档记录)')
"

echo "==> [3/4] 提交变更..."
changed=$(git status --porcelain | wc -l | tr -d ' ')
if [ "$changed" -eq 0 ]; then
    echo "    没有变更，无需提交"
    exit 0
fi

msg="${1:-daily update $(date +%Y-%m-%d)}"
git add -A
git commit -m "$msg"
echo "    提交: $msg"

echo "==> [4/4] 推送到远程..."
if git remote -v | grep -q origin; then
    git push origin main
    echo "    推送完成！"
else
    echo "    未配置远程仓库，跳过推送"
fi

echo ""
echo "✅ 部署完成！访问 https://jason-gao.github.io/daily-game-dev-news/ 查看更新"
