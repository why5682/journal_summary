# -*- coding: utf-8 -*-
"""Test actual collector module directly"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

# Direct import
import feedparser
import logging
import re
import html
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)

def fetch_papers(url, months_back=1, max_papers=10):
    """Direct copy of collector logic"""
    feed = feedparser.parse(url)
    papers = []
    cutoff_date = datetime.now() - timedelta(days=months_back * 30)
    
    for entry in feed.entries:
        # Parse publication date
        pub_date_str = (
            entry.get("published", "") or 
            entry.get("updated", "") or
            entry.get("prism_publicationdate", "") or
            ""
        )
        pub_date = None
        
        if pub_date_str:
            try:
                pub_date = date_parser.parse(pub_date_str)
                if pub_date.replace(tzinfo=None) < cutoff_date:
                    continue  # Skip old papers
            except Exception:
                pass
        
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        abstract = entry.get("summary", "") or entry.get("description", "")
        
        if title and link:
            papers.append({
                "title": title,
                "link": link,
                "abstract": abstract[:200],
                "published": pub_date_str
            })
    
    return papers[:max_papers]


feeds = {
    'JAMA': 'https://jamanetwork.com/rss/site_3/67.xml',
    'Lancet': 'https://www.thelancet.com/rssfeed/lancet_current.xml',
    'BMJ': 'https://www.bmj.com/rss/recent.xml'
}

for name, url in feeds.items():
    print(f"\n=== {name} ===")
    papers = fetch_papers(url, months_back=1, max_papers=10)
    print(f"Papers found: {len(papers)}")
    
    if papers:
        for i, p in enumerate(papers[:3], 1):
            title_short = p['title'][:40].encode('ascii', 'ignore').decode()
            print(f"  {i}. {title_short}...")
    else:
        print("  (No papers)")
