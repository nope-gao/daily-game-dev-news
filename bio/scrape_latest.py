#!/usr/bin/env python3
"""Check ScienceDaily for the very latest articles (July 20-21 specific)."""
import urllib.request, re, html, json, sys
from datetime import datetime

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

# Direct check of latest releases
pages = [
    "https://www.sciencedaily.com/news/health_medicine/",
    "https://www.sciencedaily.com/news/health_medicine/cancer/",
    "https://www.sciencedaily.com/news/health_medicine/genes/",
]

target_dates = ["2026/07/21", "2026/07/20"]
results = []

for url in pages:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='replace')
        for m in re.finditer(r'href="(/releases/[^"]+)"[^>]*>(.*?)</a>', content, re.DOTALL):
            url_suffix = m.group(1)
            title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            full_url = f"https://www.sciencedaily.com{url_suffix}"
            # Check if from target dates
            for td in target_dates:
                if td in full_url:
                    results.append((full_url, title))
                    break
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)

# Deduplicate
seen = set()
unique = []
for url, title in results:
    if url not in seen:
        seen.add(url)
        unique.append((url, title))

for url, title in unique:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            article = resp.read().decode('utf-8', errors='replace')
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', article, re.DOTALL)
        full_title = html.unescape(re.sub(r'<[^>]+>', '', h1.group(1))).strip() if h1 else title
        desc = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', article)
        summary = html.unescape(desc.group(1)).strip() if desc else ""
        
        date_match = re.search(r'/releases/20\d{2}/\d{2}/(\d{2})(\d{2})(\d{2})', url)
        article_date = ""
        if date_match:
            yy, mm, dd = date_match.group(1), date_match.group(2), date_match.group(3)
            article_date = f"20{yy}-{mm}-{dd}"
        
        print(f"=== {article_date} ===", file=sys.stderr)
        print(f"Title: {full_title}", file=sys.stderr)
        print(f"URL: {url}", file=sys.stderr)
        print(f"Summary: {summary[:200]}", file=sys.stderr)
        print(file=sys.stderr)
        
        results.append({
            "title": full_title,
            "url": url,
            "summary": summary[:600],
            "date": article_date,
        })
    except Exception as e:
        print(f"ERROR detail: {e}", file=sys.stderr)

print(json.dumps(results, ensure_ascii=False, indent=2))
