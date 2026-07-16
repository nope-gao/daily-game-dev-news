#!/usr/bin/env python3
"""News-Medical.net 最新新闻搜索"""
import urllib.request, re, html, json, sys
from datetime import datetime, timedelta

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

# 获取今天和最近的日期
today = datetime.now()
dates_to_check = [(today - timedelta(days=i)).strftime("%Y%m%d") for i in range(7)]  # 过去7天
date_strs = "|".join(dates_to_check)

urls = [
    "https://www.news-medical.net/",
    "https://www.news-medical.net/category/Life-Sciences.aspx",
    "https://www.news-medical.net/category/Genetics.aspx",
    "https://www.news-medical.net/category/Cancer.aspx",
]

found = {}
for url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='replace')
        
        # 提取文章链接: /news/YYYYMMDD...
        for m in re.finditer(r'href="(/news/(\d{8})[^"]*)"', content):
            full_url = f"https://www.news-medical.net{m.group(1)}"
            date_str = m.group(2)
            if date_str in dates_to_check:
                if full_url not in found:
                    found[full_url] = date_str
    except Exception as e:
        print(f"Warning: {url} -> {e}", file=sys.stderr)

print(f"Found {len(found)} recent articles", file=sys.stderr)

# 获取详情
results = []
for full_url in list(found.keys())[:15]:
    date_str = found[full_url]
    try:
        req = urllib.request.Request(full_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            article = resp.read().decode('utf-8', errors='replace')
        
        # Title
        title_m = re.search(r'<h1[^>]*>(.*?)</h1>', article, re.DOTALL)
        title = html.unescape(re.sub(r'<[^>]+>', '', title_m.group(1)).strip()) if title_m else ""
        
        # Meta description
        desc_m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', article)
        description = html.unescape(desc_m.group(1)).strip() if desc_m else ""
        
        # Date from URL
        pub_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        
        if title and len(title) > 10:
            results.append({
                "url": full_url,
                "title": title,
                "description": description,
                "date": pub_date,
            })
    except Exception as e:
        print(f"Error: {full_url} -> {e}", file=sys.stderr)

print(json.dumps(results, ensure_ascii=False, indent=2))
