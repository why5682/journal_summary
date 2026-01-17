"""
Medical Literature Summarizer
Streamlit app for AI-powered medical paper summarization.
"""
import streamlit as st
from datetime import datetime
import os
import sys
import markdown

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import PaperCollector, PaperSummarizer, PaperStorage
from config import JOURNALS, get_journals_by_category, get_journal_names

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

st.set_page_config(
    page_title="Medical Literature Summarizer",
    page_icon="📚",
    layout="wide"
)


def get_secret(key: str, default: str = "") -> str:
    """Safely retrieve secrets with fallback to environment variables."""
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


def main():
    st.title("📚 Medical Literature Summarizer")
    st.markdown("Get AI-powered summaries of the latest research from top medical journals.")

    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model configuration
        default_model = get_secret("OLLAMA_MODEL", "gptoss-120b:cloud")
        model_name = st.text_input("Ollama Model", value=default_model)
        
        # Time period selection
        months_back = st.selectbox(
            "Time Period",
            options=[1, 2, 3],
            format_func=lambda x: f"Last {x} month{'s' if x > 1 else ''}",
            index=0
        )
        
        # Skip duplicates option
        skip_duplicates = st.checkbox("Skip Already Processed Papers", value=True)
        
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
        
        # Storage stats
        storage = PaperStorage()
        processed_count = storage.get_processed_count()
        st.metric("Processed Papers", processed_count)
        
        if st.button("🗑️ Clear History", use_container_width=True):
            storage.clear_history()
            st.rerun()

    # Journal Selection
    st.subheader("📰 Select Journals")
    
    # Show categories
    categories = get_journals_by_category()
    with st.expander("ℹ️ Available Journals by Category", expanded=False):
        for cat, journals in categories.items():
            st.markdown(f"**{cat}:**")
            for j in journals:
                st.markdown(f"- {j['name']}")
    
    # Multiselect
    journal_names = get_journal_names()
    default_selection = ["Pharmacoepidemiology and Drug Safety"]
    
    selected_journal_names = st.multiselect(
        "Choose one or more journals",
        options=journal_names,
        default=[n for n in default_selection if n in journal_names],
        help="Select multiple journals to fetch and summarize papers from all of them"
    )
    
    if not selected_journal_names:
        st.warning("⚠️ Please select at least one journal")
        st.stop()
    
    selected_journals = [j for j in JOURNALS if j["name"] in selected_journal_names]

    # Fetch and Summarize Button
    if st.button("🚀 Fetch & Summarize Papers", type="primary", use_container_width=True):
        if not ollama_api_key:
            st.error("⚠️ OLLAMA_API_KEY not configured. Please add it to Streamlit Secrets.")
            st.info("Get your API key from: https://ollama.com/settings/keys")
            st.stop()
        
        # Initialize modules
        collector = PaperCollector()
        summarizer = PaperSummarizer(api_key=ollama_api_key, model=model_name)
        storage = PaperStorage()
        
        # Fetch papers from all selected journals
        all_papers = []
        
        with st.status(f"Fetching papers from {len(selected_journals)} journal(s)...", expanded=True) as status:
            for journal in selected_journals:
                status.write(f"📡 Fetching from {journal['name']}...")
                papers = collector.fetch_papers(journal["url"], months_back)
                
                # Add source journal to each paper
                for paper in papers:
                    paper['source'] = journal['name']
                    paper['category'] = journal.get('category', 'Other')
                    
                    # Skip if already processed
                    if skip_duplicates and storage.is_processed(paper['link']):
                        continue
                    
                    all_papers.append(paper)
                
                status.write(f"✅ Found papers from {journal['name']}")
            
            if not all_papers:
                status.update(label="No new papers found", state="error")
                st.warning("No new papers found. Try a different time period or disable 'Skip Already Processed Papers'.")
                st.stop()
            
            status.write(f"📊 Total new papers: {len(all_papers)}")
            status.write("🤖 Summarizing with AI...")
            
            summaries = []
            progress_bar = st.progress(0)
            
            for i, paper in enumerate(all_papers):
                status.write(f"Summarizing [{paper['source']}]: {paper['title'][:50]}...")
                
                ai_summary = summarizer.summarize(paper['title'], paper['abstract'])
                paper['ai_summary'] = ai_summary
                summaries.append(paper)
                
                # Save to storage
                storage.add_paper(
                    paper_id=paper['link'],
                    title=paper['title'],
                    journal=paper['source'],
                    summary=ai_summary
                )
                
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
                first_journal = list(journals_data.keys())[0]
                with st.expander(f"📄 {i}. {paper['title']}", expanded=(i==1 and journal_name==first_journal)):
                    st.caption(f"**Published:** {paper['published']} | **Category:** {paper.get('category', 'N/A')}")
                    st.markdown("### AI Summary")
                    st.info(paper['ai_summary'])
                    st.markdown(f"[🔗 Read Full Paper]({paper['link']})")
        
        # Download button
        st.divider()
        st.subheader("📥 Download Summary Report")
        
        html_data = generate_html_report(journals_data, selected_journal_names, months_back)
        
        st.download_button(
            label="📄 Download Complete Report (HTML)",
            data=html_data,
            file_name=f"medical_summary_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True
        )
        
        # Store in session state
        st.session_state['last_summaries'] = summaries
        st.session_state['last_journals'] = selected_journal_names
        st.session_state['journals_data'] = journals_data

    # Show previous results if available
    elif 'journals_data' in st.session_state:
        st.info(f"📋 Showing previous results from {len(st.session_state.get('last_journals', []))} journal(s)")
        display_cached_results()


def generate_html_report(journals_data, journal_names, months_back):
    """Generate downloadable HTML report with proper styling."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medical Literature Summary</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f8f9fa;
        }}
        h1 {{
            color: #1a1a2e;
            border-bottom: 3px solid #4a6fa5;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .meta {{
            background: #e8f4f8;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            font-size: 0.95em;
        }}
        .meta p {{ margin: 5px 0; }}
        h2 {{
            color: #2c3e50;
            margin: 30px 0 20px;
            padding: 10px 0;
            border-bottom: 2px solid #bdc3c7;
        }}
        .paper {{
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .paper h3 {{
            color: #34495e;
            font-size: 1.1em;
            margin-bottom: 10px;
        }}
        .paper-meta {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 15px;
        }}
        .summary {{
            background: #f0f7ff;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 8px 8px 0;
        }}
        .summary table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 0.9em;
        }}
        .summary th, .summary td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        .summary th {{
            background: #4a6fa5;
            color: white;
        }}
        .summary tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        .summary ul, .summary ol {{
            margin: 10px 0 10px 20px;
        }}
        .summary strong {{
            color: #2c3e50;
        }}
        .paper a {{
            display: inline-block;
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
            margin-top: 10px;
        }}
        .paper a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>📚 Medical Literature Summary</h1>
    <div class="meta">
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Journals:</strong> {', '.join(journal_names)}</p>
        <p><strong>Time Period:</strong> Last {months_back} month{'s' if months_back > 1 else ''}</p>
    </div>
"""
    
    for journal_name, papers in journals_data.items():
        html += f'    <h2>📰 {journal_name} ({len(papers)} papers)</h2>\n'
        for i, paper in enumerate(papers, 1):
            # Escape HTML characters in title only
            title = paper['title'].replace('<', '&lt;').replace('>', '&gt;')
            # Convert markdown in summary to HTML (for tables, lists, bold, etc.)
            summary_html = markdown.markdown(
                paper['ai_summary'], 
                extensions=['tables', 'fenced_code']
            )
            
            html += f'''    <div class="paper">
        <h3>{i}. {title}</h3>
        <p class="paper-meta">Published: {paper['published']}</p>
        <div class="summary">{summary_html}</div>
        <a href="{paper['link']}" target="_blank">🔗 Read Full Paper</a>
    </div>
'''
    
    html += """</body>
</html>"""
    
    return html


def display_cached_results():
    """Display previously fetched results from session state."""
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
    
    html_data = generate_html_report(
        journals_data, 
        st.session_state.get('last_journals', []),
        1
    )
    
    st.download_button(
        label="📄 Download Complete Report (HTML)",
        data=html_data,
        file_name=f"medical_summary_{datetime.now().strftime('%Y%m%d')}.html",
        mime="text/html",
        use_container_width=True
    )


if __name__ == "__main__":
    main()
