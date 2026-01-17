"""
RSS Feed Collector Module
Fetches and parses papers from medical journal RSS feeds.
"""
import feedparser
import logging
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class PaperCollector:
    """Handles fetching and parsing of RSS feeds."""

    def __init__(self, user_agent: str = "MedicalSummarizer/1.0"):
        self.user_agent = user_agent

    def fetch_papers(
        self, 
        url: str, 
        months_back: int = 1,
        max_papers: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches papers from an RSS feed within specified date range.
        
        Args:
            url: RSS feed URL
            months_back: Number of months to look back
            max_papers: Maximum number of papers to return (None for all)
            
        Returns:
            List of paper dictionaries
        """
        logger.info(f"Fetching RSS feed: {url}")
        
        try:
            feed = feedparser.parse(url, agent=self.user_agent)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning: {feed.bozo_exception}")

            papers = []
            cutoff_date = datetime.now() - timedelta(days=months_back * 30)

            for entry in feed.entries:
                paper = self._parse_entry(entry, cutoff_date)
                if paper:
                    papers.append(paper)
                    
                    if max_papers and len(papers) >= max_papers:
                        break

            logger.info(f"Found {len(papers)} papers from feed")
            return papers

        except Exception as e:
            logger.error(f"Error fetching feed {url}: {e}")
            return []

    def _parse_entry(
        self, 
        entry: Any, 
        cutoff_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """Parse a single RSS entry into a paper dict."""
        # Parse publication date
        pub_date_str = entry.get("published", "") or entry.get("updated", "")
        pub_date = None
        
        if pub_date_str:
            try:
                pub_date = date_parser.parse(pub_date_str)
                # Skip papers older than cutoff
                if pub_date.replace(tzinfo=None) < cutoff_date:
                    return None
            except Exception:
                pass  # If parsing fails, include the paper anyway

        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        abstract = (
            entry.get("description", "") or 
            entry.get("summary", "") or 
            "No abstract available"
        ).strip()

        if not title or not link:
            return None

        return {
            "title": title,
            "link": link,
            "abstract": abstract,
            "published": pub_date_str or "Unknown date",
            "parsed_date": pub_date
        }
