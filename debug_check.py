import requests
import sys
import os

# Add path to find core modeul
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.collector import PaperCollector

print("=== Diagnostic: JAMA Access ===")

url = 'https://jamanetwork.com/rss/site_3/67.xml'

# 1. Direct Requests Test (The one that worked before)
print("\n1. Testing Direct Requests (Manual Headers)...")
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}
try:
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"   Status: {resp.status_code}")
    print(f"   Content Length: {len(resp.content)}")
except Exception as e:
    print(f"   Error: {e}")

# 2. Collector Test
print("\n2. Testing Collector Class...")
try:
    c = PaperCollector()
    print("   Collector Headers:")
    for k, v in c.headers.items():
        print(f"     {k}: {v}")
    
    papers = c.fetch_papers(url)
    print(f"   Papers found: {len(papers)}")
    if not papers:
        print("   FAILED to find papers via Collector.")
except Exception as e:
    print(f"   Error: {e}")
