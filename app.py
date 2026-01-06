import streamlit as st
import feedparser
import os
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from ollama import Client

# ========================================
# Streamlit Secrets Configuration
# ========================================
# Set these in Streamlit Cloud → Settings → Secrets:
#
# OLLAMA_API_KEY = "your_ollama_cloud_api_key"
# OLLAMA_MODEL = "gptoss-120b:cloud"
#
# Get your API key from: https://ollama.com/settings/keys
# ========================================

# Page Config
st.set_page_config(
    page_title="Top Medical Journals Summarizer",
    page_icon="📚",
    layout="wide"
)

# Journal RSS Feeds - Focus on Pharmacoepidemiology
JOURNALS = [
    {
        "name": "The BMJ",
        "url": "https://www.bmj.com/rss/research.xml",
        "category": "General Medical"
    },
    {
        "name": "The Lancet",
        "url": "https://www.thelancet.com/rssfeed/lancet_current.xml",
        "category": "General Medical"
    },
    {
        "name": "NEJM",
        "url": "https://www.nejm.org/action/showFeed?type=etoc&feed=rss&jc=nejm",
        "category": "General Medical"
    },
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
    {
        "name": "JAMA",
        "url": "https://jamanetwork.com/rss/site_5/161.xml",
        "category": "General Medical"
    },
    {
        "name": "Annals of Internal Medicine",
        "url": "https://www.acpjournals.org/rss/site_5/135.xml",
        "category": "General Medical"
    }
]

def get_secret(key: str, default: str = "") -> str:
    """Safely retrieve secrets with fallback to environment variables."""
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)

def fetch_papers_from_rss(journal_url: str, months_back: int = 1):
    """Fetch papers from RSS feed within specified date range."""
    try:
        feed = feedparser.parse(journal_url)
        papers = []
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=months_back * 30)
        
        for entry in feed.entries:
            # Parse publication date
            pub_date_str = entry.get("published", "")
            pub_date = None
            
            if pub_date_str:
                try:
                    # Try to parse the date
                    pub_date = date_parser.parse(pub_date_str)
                except:
                    # If parsing fails, skip date filtering
                    pub_date = None
            
            # Filter by date if we could parse it
            if pub_date and pub_date < cutoff_date:
                continue  # Skip papers older than cutoff
            
            paper = {
                "title": entry.get("title", "No title"),
                "link": entry.get("link", ""),
                "published": pub_date_str or "Unknown date",
                "summary": entry.get("summary", "No abstract available"),
                "parsed_date": pub_date
            }
            papers.append(paper)
        
        return papers
    except Exception as e:
        st.error(f"Failed to fetch RSS: {e}")
        return []

def summarize_paper(title: str, abstract: str, ollama_client, model: str):
    """Summarize a paper using Ollama Cloud."""
    prompt = f"""
You are a medical researcher. Summarize the following research paper in a concise, professional manner.

Title: {title}

Abstract: {abstract}

Provide a summary that includes:
1. Main objective
2. Key findings
3. Clinical significance

Keep it to 3-4 sentences, suitable for busy clinicians.
"""
    
    try:
        response = ollama_client.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        return response['message']['content']
    except Exception as e:
        return f"⚠️ Summarization failed: {str(e)}"

def export_summaries_as_markdown(summaries, journal_name):
    """Export summaries as Markdown."""
    md = f"# {journal_name} - Recent Papers Summary\n"
    md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md += "---\n\n"
    
    for i, paper in enumerate(summaries, 1):
        md += f"## {i}. {paper['title']}\n\n"
        md += f"**Published:** {paper['published']}\n\n"
        md += f"### Summary\n{paper['ai_summary']}\n\n"
        md += f"[Read Full Paper]({paper['link']})\n\n"
        md += "---\n\n"
    
    return md

def main():
    st.title("📚 Top Medical Journals Summarizer")
    st.markdown("Get AI-powered summaries of the latest research from top medical journals.")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model configuration
        default_model = get_secret("OLLAMA_MODEL", "gptoss-120b:cloud")
        model_name = st.text_input("Ollama Model", value=default_model)
        
        # Date range selection
        months_back = st.selectbox(
            "Time Period",
            options=[1, 2, 3],
            format_func=lambda x: f"Last {x} month{'s' if x > 1 else ''}",
            index=0
        )
        
        st.divider()
        
        # API Key Status
        ollama_api_key = get_secret("OLLAMA_API_KEY", "")
        
        st.subheader("📋 Status")
        if ollama_api_key:
            st.success("✅ Ollama API Key Configured")
        else:
            st.error("❌ Missing Ollama API Key")
            st.caption("Add `OLLAMA_API_KEY` to Secrets")
            st.caption("[Get key](https://ollama.com/settings/keys)")

    # Journal selection with categories
    st.subheader("📰 Select Journals")
    
    # Group journals by category
    categories = {}
    for journal in JOURNALS:
        cat = journal.get("category", "Other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(journal["name"])
    
    # Show categories
    with st.expander("ℹ️ Available Journals by Category", expanded=False):
        for cat, journals in categories.items():
            st.markdown(f"**{cat}:**")
            for j in journals:
                st.markdown(f"- {j}")
    
    # Multiselect
    journal_names = [j["name"] for j in JOURNALS]
    selected_journal_names = st.multiselect(
        "Choose one or more journals",
        options=journal_names,
        default=[journal_names[3]] if len(journal_names) > 3 else [journal_names[0]],  # Default to Pharmacoepidemiology journal
        help="Select multiple journals to fetch and summarize papers from all of them"
    )
    
    if not selected_journal_names:
        st.warning("⚠️ Please select at least one journal")
        st.stop()
    
    selected_journals = [j for j in JOURNALS if j["name"] in selected_journal_names]

    # Fetch and Summarize Button
    if st.button("🚀 Fetch & Summarize Papers", type="primary"):
        if not ollama_api_key:
            st.error("⚠️ OLLAMA_API_KEY not configured. Please add it to Streamlit Secrets.")
            st.info("Get your API key from: https://ollama.com/settings/keys")
            st.stop()
        
        # Initialize Ollama Client
        try:
            ollama_client = Client(
                host='https://ollama.com',
                headers={'Authorization': f'Bearer {ollama_api_key}'}
            )
        except Exception as e:
            st.error(f"Failed to initialize Ollama client: {e}")
            st.stop()
        
        # Fetch papers from all selected journals
        all_papers = []
        
        with st.status(f"Fetching papers from {len(selected_journals)} journal(s)...", expanded=True) as status:
            for journal in selected_journals:
                status.write(f"📡 Fetching from {journal['name']}...")
                papers = fetch_papers_from_rss(journal["url"], months_back)
                
                # Add source journal to each paper
                for paper in papers:
                    paper['source'] = journal['name']
                    paper['category'] = journal.get('category', 'Other')
                
                all_papers.extend(papers)
                status.write(f"✅ Found {len(papers)} papers from {journal['name']}")
            
            if not all_papers:
                status.update(label="No papers found", state="error")
                st.error("No papers found in selected journals. Try a different time period.")
                st.stop()
            
            status.write(f"📊 Total papers found: {len(all_papers)}")
            status.write("🤖 Summarizing with AI...")
            
            summaries = []
            progress_bar = st.progress(0)
            
            for i, paper in enumerate(all_papers):
                status.write(f"Summarizing [{paper['source']}]: {paper['title'][:50]}...")
                
                ai_summary = summarize_paper(
                    paper['title'],
                    paper['summary'],
                    ollama_client,
                    model_name
                )
                
                paper['ai_summary'] = ai_summary
                summaries.append(paper)
                
                progress_bar.progress((i + 1) / len(all_papers))
            
            status.update(label="✅ All papers summarized!", state="complete", expanded=False)
        
        # Display results
        st.success(f"📊 Successfully summarized {len(summaries)} papers from {len(selected_journals)} journal(s)")
        
        # Group by journal
        journals_data = {}
        for paper in summaries:
            source = paper['source']
            if source not in journals_data:
                journals_data[source] = []
            journals_data[source].append(paper)
        
        # Show summaries grouped by journal
        for journal_name, papers in journals_data.items():
            st.markdown(f"### 📚 {journal_name} ({len(papers)} papers)")
            
            for i, paper in enumerate(papers, 1):
                with st.expander(f"📄 {i}. {paper['title']}", expanded=(i==1 and journal_name==list(journals_data.keys())[0])):
                    st.caption(f"**Published:** {paper['published']} | **Category:** {paper.get('category', 'N/A')}")
                    st.markdown("### AI Summary")
                    st.info(paper['ai_summary'])
                    st.markdown(f"[🔗 Read Full Paper]({paper['link']})")
        
        # Download button
        st.divider()
        st.subheader("📥 Download Summary Report")
        
        # Generate combined report
        md_data = f"# Medical Literature Summary - Multiple Journals\n"
        md_data += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        md_data += f"**Journals:** {', '.join(selected_journal_names)}\n"
        md_data += f"**Time Period:** Last {months_back} month{'s' if months_back > 1 else ''}\n\n"
        md_data += "---\n\n"
        
        for journal_name, papers in journals_data.items():
            md_data += f"## {journal_name}\n\n"
            for i, paper in enumerate(papers, 1):
                md_data += f"### {i}. {paper['title']}\n\n"
                md_data += f"**Published:** {paper['published']}\n\n"
                md_data += f"**Summary:**\n{paper['ai_summary']}\n\n"
                md_data += f"[Read Full Paper]({paper['link']})\n\n"
                md_data += "---\n\n"
        
        st.download_button(
            label="📄 Download Complete Report (Markdown)",
            data=md_data,
            file_name=f"medical_summary_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True
        )
        
        # Store in session state for persistence
        st.session_state['last_summaries'] = summaries
        st.session_state['last_journals'] = selected_journal_names
        st.session_state['journals_data'] = journals_data

    # Show previous results if available
    elif 'journals_data' in st.session_state:
        st.info(f"📋 Showing previous results from {len(st.session_state.get('last_journals', []))} journal(s)")
        
        journals_data = st.session_state['journals_data']
        
        for journal_name, papers in journals_data.items():
            st.markdown(f"### 📚 {journal_name} ({len(papers)} papers)")
            
            for i, paper in enumerate(papers, 1):
                with st.expander(f"📄 {i}. {paper['title']}", expanded=False):
                    st.caption(f"**Published:** {paper['published']} | **Category:** {paper.get('category', 'N/A')}")
                    st.markdown("### AI Summary")
                    st.info(paper['ai_summary'])
                    st.markdown(f"[🔗 Read Full Paper]({paper['link']})")
        
        # Download button for cached results
        st.divider()
        
        md_data = f"# Medical Literature Summary - Multiple Journals\n"
        md_data += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        md_data += f"**Journals:** {', '.join(st.session_state.get('last_journals', []))}\n\n"
        md_data += "---\n\n"
        
        for journal_name, papers in journals_data.items():
            md_data += f"## {journal_name}\n\n"
            for i, paper in enumerate(papers, 1):
                md_data += f"### {i}. {paper['title']}\n\n"
                md_data += f"**Published:** {paper['published']}\n\n"
                md_data += f"**Summary:**\n{paper['ai_summary']}\n\n"
                md_data += f"[Read Full Paper]({paper['link']})\n\n"
                md_data += "---\n\n"
        
        st.download_button(
            label="📄 Download Complete Report (Markdown)",
            data=md_data,
            file_name=f"medical_summary_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
