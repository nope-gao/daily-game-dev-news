#!/usr/bin/env python3
"""Scrape News-Medical.net for latest bio/health news."""
import urllib.request, re, html, json, sys
from datetime import datetime

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

# Main page and specific topic pages
pages = [
    "https://www.news-medical.net/",
    "https://www.news-medical.net/medical/long-reads",
    "https://www.news-medical.net/medical/thought-leadership",
]

all_links = set()
current_month = "202607"  # YYYYMM format for News-Medical URLs

for url in pages:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='replace')
        # News-Medical news links: href="/news/YYYYMMDD..."
        for m in re.finditer(r'href="(/news/(\d{8})[^"]*)"', content):
            full_url = f"https://www.news-medical.net{m.group(1)}"
            date_str = m.group(2)
            # Extract title from the link context
            all_links.add((full_url, date_str))
    except Exception as e:
        print(f"ERROR fetching {url}: {e}", file=sys.stderr)

# Filter: only this month
current_links = [(u, d) for u, d in all_links if d.startswith(current_month)]
print(f"Found {len(current_links)} current-month links", file=sys.stderr)

# Fetch details
results = []
for full_url, date_str in list(current_links)[:15]:
    try:
        req = urllib.request.Request(full_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html_content = resp.read().decode('utf-8', errors='replace')

        # Title
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL)
        title = html.unescape(re.sub(r'<[^>]+>', '', title_match.group(1))).strip() if title_match else ""

        # Meta description (most reliable for News-Medical)
        desc_match = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', html_content)
        description = html.unescape(desc_match.group(1)).strip() if desc_match else ""

        if title and description:
            article_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            results.append({
                "title": title,
                "url": full_url,
                "summary": description[:600],
                "date": article_date,
            })
    except Exception as e:
        print(f"ERROR {full_url}: {e}", file=sys.stderr)

print(json.dumps(results, ensure_ascii=False, indent=2))
