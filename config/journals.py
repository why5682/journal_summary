"""
Journal Configuration
Defines available medical journals and their RSS feeds.
"""

JOURNALS = [
    # Pharmacoepidemiology (Primary Focus)
    {
        "name": "Pharmacoepidemiology and Drug Safety",
        "url": "https://onlinelibrary.wiley.com/feed/10991557/most-recent",
        "category": "Pharmacoepidemiology"
    },
    {
        "name": "Drug Safety",
        "url": "https://link.springer.com/search.rss?facet-content-type=Article&facet-journal-id=40264&channel-name=Drug%20Safety",
        "category": "Pharmacoepidemiology"
    },
    
    # Clinical Pharmacology
    {
        "name": "Clinical Pharmacology & Therapeutics",
        "url": "https://onlinelibrary.wiley.com/feed/15326535/most-recent",
        "category": "Clinical Pharmacology"
    },
    {
        "name": "British Journal of Clinical Pharmacology",
        "url": "https://onlinelibrary.wiley.com/feed/13652125/most-recent",
        "category": "Clinical Pharmacology"
    },
    
    # General Medical (Top Tier)
    {
        "name": "NEJM",
        "url": "https://www.nejm.org/action/showFeed?type=etoc&feed=rss&jc=nejm",
        "category": "General Medical"
    },
    {
        "name": "The Lancet",
        "url": "https://www.thelancet.com/rssfeed/lancet_current.xml",
        "category": "General Medical"
    },
    {
        "name": "JAMA",
        "url": "https://jamanetwork.com/rss/site_5/161.xml",
        "category": "General Medical"
    },
    {
        "name": "The BMJ",
        "url": "https://www.bmj.com/rss/research.xml",
        "category": "General Medical"
    },
    {
        "name": "Annals of Internal Medicine",
        "url": "https://www.acpjournals.org/rss/site_5/135.xml",
        "category": "General Medical"
    }
]


def get_journals_by_category():
    """Group journals by category."""
    categories = {}
    for journal in JOURNALS:
        cat = journal.get("category", "Other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(journal)
    return categories


def get_journal_names():
    """Get list of all journal names."""
    return [j["name"] for j in JOURNALS]
