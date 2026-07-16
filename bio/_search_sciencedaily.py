#!/usr/bin/env python3
"""ScienceDaily 生物/健康新闻搜索脚本"""
import urllib.request, re, html, json, sys
from datetime import datetime

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

# 抓取健康医学相关板块
pages = [
    "https://www.sciencedaily.com/news/health_medicine/",
    "https://www.sciencedaily.com/news/health_medicine/cancer/",
    "https://www.sciencedaily.com/news/health_medicine/genes/",
    "https://www.sciencedaily.com/news/health_medicine/fitness/",
    "https://www.sciencedaily.com/news/health_medicine/heart_disease/",
]

all_links = {}  # url -> title (use dict to deduplicate)
current_month = datetime.now().strftime("%Y/%m/")  # e.g., "2026/07/"

for url in pages:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='replace')
        
        for m in re.finditer(r'href="(/releases/[^"]+)"[^>]*>(.*?)</a>', content, re.DOTALL):
            url_suffix = m.group(1)
            raw_title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            raw_title = html.unescape(raw_title)
            if raw_title and len(raw_title) > 15:
                full_url = f"https://www.sciencedaily.com{url_suffix}"
                if full_url not in all_links:
                    all_links[full_url] = raw_title
    except Exception as e:
        print(f"Warning: {url} -> {e}", file=sys.stderr)

# 过滤：只保留当前月的文章
current_links = [(u, t) for u, t in all_links.items() if current_month in u]
target_links = current_links if len(current_links) >= 12 else list(all_links.items())

print(f"Total links found: {len(all_links)}", file=sys.stderr)
print(f"Current month ({current_month}) links: {len(current_links)}", file=sys.stderr)
print(f"Target links to fetch: {len(target_links)}", file=sys.stderr)

# 逐个抓取详情
results = []
for full_url, title in target_links[:18]:
    try:
        req = urllib.request.Request(full_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            article = resp.read().decode('utf-8', errors='replace')
        
        # Extract title
        title_m = re.search(r'<h1[^>]*>(.*?)</h1>', article, re.DOTALL)
        article_title = html.unescape(re.sub(r'<[^>]+>', '', title_m.group(1)).strip()) if title_m else title
        
        # Extract meta description
        desc_m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', article)
        description = html.unescape(desc_m.group(1)).strip() if desc_m else ""
        
        # Extract lead paragraph
        lead_m = re.search(r'class="lead"[^>]*>(.*?)</div>', article, re.DOTALL)
        lead = html.unescape(re.sub(r'<[^>]+>', '', lead_m.group(1)).strip()) if lead_m else ""
        
        # Extract paragraphs for body text
        pars = re.findall(r'<p[^>]*>(.*?)</p>', article, re.DOTALL)
        body_pars = []
        for p in pars:
            text = html.unescape(re.sub(r'<[^>]+>', '', p)).strip()
            if len(text) > 50:
                body_pars.append(text)
        body = "\n".join(body_pars[:6])
        
        # Extract date from URL
        date_m = re.search(r'/releases/(\d{4})/(\d{2})/(\d{2})', full_url)
        if date_m:
            pub_date = f"{date_m.group(1)}-{date_m.group(2)}-{date_m.group(3)}"
        else:
            pub_date = ""
        
        results.append({
            "url": full_url,
            "title": article_title,
            "description": description,
            "lead": lead,
            "body": body[:500],
            "date": pub_date,
        })
    except Exception as e:
        print(f"Error fetching {full_url}: {e}", file=sys.stderr)

# Output as JSON
print(json.dumps(results, ensure_ascii=False, indent=2))
