#!/usr/bin/env python3
"""Scrape ScienceDaily health/medicine sections for bio daily news."""
import urllib.request, re, html, json, sys
from datetime import datetime

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

pages = [
    "https://www.sciencedaily.com/news/health_medicine/",
    "https://www.sciencedaily.com/news/health_medicine/cancer/",
    "https://www.sciencedaily.com/news/health_medicine/genes/",
    "https://www.sciencedaily.com/news/health_medicine/fitness/",
    "https://www.sciencedaily.com/news/health_medicine/diet_and_weight_loss/",
    "https://www.sciencedaily.com/news/health_medicine/heart_disease/",
]

all_links = set()
current_month = datetime.now().strftime("%Y/%m/")

for url in pages:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='replace')
        for m in re.finditer(r'href="(/releases/[^"]+)"[^>]*>(.*?)</a>', content, re.DOTALL):
            url_suffix = m.group(1)
            title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            if title and len(title) > 15:
                full_url = f"https://www.sciencedaily.com{url_suffix}"
                all_links.add((full_url, title))
    except Exception as e:
        print(f"ERROR fetching {url}: {e}", file=sys.stderr)

all_links = list(all_links)

# Filter to current month
current_links = [(u, t) for u, t in all_links if current_month in u]
target = current_links if len(current_links) >= 10 else all_links
print(f"Found {len(target)} current-month links", file=sys.stderr)

# Fetch details for up to 25 articles
results = []
for full_url, link_title in target[:25]:
    try:
        req = urllib.request.Request(full_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            article = resp.read().decode('utf-8', errors='replace')

        # Title from h1
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', article, re.DOTALL)
        title = html.unescape(re.sub(r'<[^>]+>', '', h1_match.group(1))).strip() if h1_match else link_title

        # Meta description
        desc_match = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', article)
        description = html.unescape(desc_match.group(1)).strip() if desc_match else ""

        # Lead paragraph
        lead_match = re.search(r'class="lead"[^>]*>(.*?)</div>', article, re.DOTALL)
        lead = html.unescape(re.sub(r'<[^>]+>', '', lead_match.group(1))).strip() if lead_match else ""

        # Date from URL
        date_match = re.search(r'/releases/20\d{2}/\d{2}/(\d{2})(\d{2})(\d{2})', full_url)
        article_date = ""
        if date_match:
            yy, mm, dd = date_match.group(1), date_match.group(2), date_match.group(3)
            article_date = f"20{yy}-{mm}-{dd}"

        # Extract paragraphs
        pars = re.findall(r'<p[^>]*>(.*?)</p>', article, re.DOTALL)
        clean_pars = []
        for p in pars:
            clean = html.unescape(re.sub(r'<[^>]+>', '', p)).strip()
            if len(clean) > 80 and not any(s in clean.lower() for s in ['copyright', 'all rights reserved', 'related stories', 'story source:', 'journal reference:', 'subscribe to']):
                clean_pars.append(clean)

        # Build summary: use lead first, then first long paragraph, then description
        summary = lead if len(lead) > 80 else ""
        if len(summary) < 80 and clean_pars:
            for p in clean_pars[:3]:
                if len(p) > 100:
                    summary = p
                    break
        if len(summary) < 80 and description:
            summary = description

        results.append({
            "title": title,
            "url": full_url,
            "summary": summary[:600],
            "date": article_date,
            "description": description[:300],
        })
    except Exception as e:
        print(f"ERROR fetching {full_url}: {e}", file=sys.stderr)

print(json.dumps(results, ensure_ascii=False, indent=2))
