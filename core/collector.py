"""
RSS Feed Collector Module
Fetches and parses papers from medical journal RSS feeds.
Includes journal-specific parsing and HTML cleanup.
"""
import feedparser
import logging
import re
import html
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class PaperCollector:
    """Handles fetching and parsing of RSS feeds with journal-specific logic."""

    def __init__(self, user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"):
        self.user_agent = user_agent

    def fetch_papers(
        self, 
        url: str, 
        months_back: int = 1,
        max_papers: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetches papers from an RSS feed within specified date range.
        Returns max_papers most recent papers, sorted by date (newest first).
        """
        logger.info(f"Fetching RSS feed: {url}")
        
        try:
            # Add request headers to bypass bot protection (JAMA need this)
            feed = feedparser.parse(
                url, 
                agent=self.user_agent,
                request_headers={'User-Agent': self.user_agent}
            )
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning: {feed.bozo_exception}")

            # Detect journal type from URL
            journal_type = self._detect_journal_type(url)
            
            papers = []
            cutoff_date = datetime.now() - timedelta(days=months_back * 30)

            for entry in feed.entries:
                paper = self._parse_entry(entry, cutoff_date, journal_type)
                if paper:
                    papers.append(paper)

            # Sort by date (newest first)
            papers.sort(
                key=lambda p: p.get('parsed_date') or datetime.min,
                reverse=True
            )
            
            # Limit to max_papers
            papers = papers[:max_papers]

            logger.info(f"Found {len(papers)} papers from feed (limited to {max_papers})")
            return papers

        except Exception as e:
            logger.error(f"Error fetching feed {url}: {e}")
            return []

    def _detect_journal_type(self, url: str) -> str:
        """Detect journal type from URL for specific parsing."""
        url_lower = url.lower()
        
        if 'wiley.com' in url_lower:
            return 'wiley'
        elif 'springer.com' in url_lower:
            return 'springer'
        elif 'nejm.org' in url_lower:
            return 'nejm'
        elif 'thelancet.com' in url_lower:
            return 'lancet'
        elif 'jamanetwork.com' in url_lower:
            return 'jama'
        elif 'bmj.com' in url_lower:
            return 'bmj'
        else:
            return 'generic'

    def _parse_entry(
        self, 
        entry: Any, 
        cutoff_date: datetime,
        journal_type: str
    ) -> Optional[Dict[str, Any]]:
        """Parse a single RSS entry with journal-specific logic."""
        
        # Parse publication date - check multiple possible date fields
        pub_date_str = (
            entry.get("published", "") or 
            entry.get("updated", "") or
            entry.get("dc_date", "") or  # BMJ uses dc:date
            entry.get("prism_publicationdate", "") or  # Lancet uses prism:publicationDate
            entry.get("pubDate", "") or  # JAMA standard
            ""
        )
        pub_date = None
        
        if pub_date_str:
            try:
                pub_date = date_parser.parse(pub_date_str)
                # Normalize to naive datetime (UTC) to safely compare/sort
                pub_date = pub_date.replace(tzinfo=None)
                
                if pub_date < cutoff_date:
                    return None
            except Exception:
                # If date parsing fails, include the paper anyway (no date filter)
                pub_date = None
                pass

        # Extract title
        title = self._clean_text(entry.get("title", ""))
        
        # Extract link
        link = entry.get("link", "").strip()
        
        # Extract abstract based on journal type
        abstract = self._extract_abstract(entry, journal_type)
        
        if not title or not link:
            return None

        return {
            "title": title,
            "link": link,
            "abstract": abstract,
            "published": pub_date_str or "Unknown date",
            "parsed_date": pub_date
        }

    def _extract_abstract(self, entry: Any, journal_type: str) -> str:
        """Extract and clean abstract based on journal type."""
        
        # Try different fields for abstract
        raw_abstract = ""
        
        if journal_type == 'wiley':
            # Wiley uses dc:description with HTML, or content:encoded
            raw_abstract = (
                entry.get("dc_description", "") or 
                entry.get("description", "") or 
                entry.get("summary", "")
            )
        elif journal_type == 'springer':
            # Springer has clean text in description
            raw_abstract = entry.get("description", "") or entry.get("summary", "")
        elif journal_type == 'nejm':
            # NEJM has brief description
            raw_abstract = entry.get("description", "") or entry.get("summary", "")
        elif journal_type == 'lancet':
            # Lancet often has minimal abstract
            raw_abstract = entry.get("description", "") or entry.get("summary", "")
        elif journal_type == 'jama':
            # JAMA has description
            raw_abstract = entry.get("description", "") or entry.get("summary", "")
        else:
            raw_abstract = (
                entry.get("description", "") or 
                entry.get("summary", "") or 
                ""
            )
        
        # Clean the abstract
        cleaned = self._clean_abstract(raw_abstract)
        
        return cleaned if cleaned else "No abstract available"

    def _clean_abstract(self, text: str) -> str:
        """Clean abstract text by removing HTML tags and normalizing whitespace."""
        if not text:
            return ""
        
        # Decode HTML entities (&amp; -> &, etc.)
        text = html.unescape(text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove "ABSTRACT" prefix if present
        text = re.sub(r'^ABSTRACT\s*', '', text, flags=re.IGNORECASE)
        
        # Remove section headers like "Purpose", "Methods", "Results", "Conclusion"
        # but keep content (replace with colon if needed for readability)
        text = re.sub(r'\b(Purpose|Objective|Background|Methods?|Results?|Conclusions?|Discussion)\b\s*:?\s*', '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text

    def _clean_text(self, text: str) -> str:
        """Clean general text (titles, etc.)."""
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags (if any)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
