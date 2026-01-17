import requests
import feedparser

url = 'https://jamanetwork.com/rss/site_3/67.xml'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

print(f"Testing JAMA access with requests...")
try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.text)}")
    
    if response.status_code == 200:
        feed = feedparser.parse(response.text)
        print(f"Feed entries: {len(feed.entries)}")
        if feed.entries:
            print(f"First title: {feed.entries[0].title}")
    else:
        print("Failed to fetch")
        print(response.text[:500])
        
except Exception as e:
    print(f"Error: {e}")
