#!/bin/bash
# ============================================
# Daily Express — 三站部署脚本
# 用法: bash deploy.sh [commit message]
# ============================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
STATIONS=("game" "bio" "world")

cd "$PROJECT_DIR"

echo "==> 三站部署: $(date +%Y-%m-%d)"

for STATION in "${STATIONS[@]}"; do
    echo ""
    echo "==> [$STATION] 检查日报..."

    DAILY_DIR="$PROJECT_DIR/$STATION/daily"
    INDEX_PATH="$PROJECT_DIR/$STATION/index.html"

    latest_html=$(ls -t "$DAILY_DIR"/*.html 2>/dev/null | head -1)

    if [ -z "$latest_html" ]; then
        echo "    无日报文件，跳过 $STATION"
        continue
    fi

    echo "    最新: $(basename "$latest_html")"

    echo "==> [$STATION] 更新存档数据..."

    python3 -c "
import os, re, json
from datetime import datetime

daily_dir = '$DAILY_DIR'
index_path = '$INDEX_PATH'
weekdays = ['星期一','星期二','星期三','星期四','星期五','星期六','星期日']

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
        print(f'    解析已有存档失败: {e}')

new_dates = set()
for f in os.listdir(daily_dir):
    dm = re.match(r'(\d{4}-\d{2}-\d{2})\.html$', f)
    if dm:
        new_dates.add(dm.group(1))

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
        keywords = ''
        filepath = os.path.join(daily_dir, date_str + '.html')
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                kw_match = re.search(r'<div class=\"keywords\">(.*?)</div>', content, re.DOTALL)
                if kw_match:
                    raw = re.sub(r'<[^>]+>', '', kw_match.group(1)).strip()
                    keywords = re.sub(r'\s+', ' ', raw)
            except Exception:
                pass
        entries.append({'date': date_str, 'weekday': weekday, 'keywords': keywords})

entries.sort(key=lambda x: x['date'], reverse=True)
js_data = json.dumps(entries, ensure_ascii=False, indent=4)
pattern = r'(var ARCHIVE_DATA\s*=\s*)\[.*?\](;)'
replacement = r'\1' + js_data + r'\2'
new_html, count = re.subn(pattern, replacement, html, flags=re.DOTALL)

if count == 0:
    print('    警告: 未找到 ARCHIVE_DATA，$STATION 未更新')
else:
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'    已更新 ({len(entries)} 条记录)')
"

done

echo ""
echo "==> 提交变更..."
changed=$(git status --porcelain | wc -l | tr -d ' ')
if [ "$changed" -eq 0 ]; then
    echo "    没有变更，无需提交"
    exit 0
fi

msg="${1:-daily update $(date +%Y-%m-%d)}"
git add -A
git commit -m "$msg"
echo "    提交: $msg"

echo "==> 推送到远程..."
if git remote -v | grep -q origin; then
    git push origin main
    echo "    推送完成！"
else
    echo "    未配置远程仓库，跳过推送"
fi

echo ""
echo "✅ 三站部署完成！https://nope-gao.github.io/ai-daily-express/"
