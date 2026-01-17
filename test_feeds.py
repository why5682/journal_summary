"""Test RSS feeds to debug date parsing issue"""
import feedparser
from dateutil import parser as date_parser
from datetime import datetime, timedelta

feeds = {
    'JAMA': 'https://jamanetwork.com/rss/site_3/67.xml',
    'PDS': 'https://onlinelibrary.wiley.com/feed/10991557/most-recent',
    'NEJM': 'https://www.nejm.org/action/showFeed?type=etoc&feed=rss&jc=nejm'
}

cutoff = datetime.now() - timedelta(days=90)  # 3 months
print(f"Current time: {datetime.now()}")
print(f"Cutoff date: {cutoff}")
print()

for name, url in feeds.items():
    feed = feedparser.parse(url)
    print(f"=== {name} ({len(feed.entries)} entries) ===")
    
    valid = 0
    for entry in feed.entries[:5]:
        title = entry.get('title', 'No title')[:50]
        pub_str = entry.get('published', '') or entry.get('updated', '')
        
        try:
            if pub_str:
                pub_date = date_parser.parse(pub_str)
                pub_naive = pub_date.replace(tzinfo=None)
                is_valid = pub_naive >= cutoff
                status = "OK" if is_valid else "FILTERED OUT"
                print(f"  [{status}] {title}...")
                print(f"    Raw: {pub_str}")
                print(f"    Parsed: {pub_naive}")
                if is_valid:
                    valid += 1
            else:
                print(f"  [NO DATE] {title}...")
        except Exception as e:
            print(f"  [ERROR] {title}: {e}")
    
    print(f"  Summary: {valid}/5 would pass filter")
    print()
