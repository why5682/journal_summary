"""
Medical Literature Trend Analyzer
Streamlit app for AI-powered trend analysis of medical research.
"""
import streamlit as st
from datetime import datetime
import os
import sys
import base64

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import PaperCollector, TrendAnalyzer
from config import JOURNALS, get_journals_by_category, get_journal_names

# RWD / Pharmacoepidemiology Keywords (Default - can be edited by user)
DEFAULT_RWD_KEYWORDS = """real-world, real world, rwd, rwe, observational
retrospective, prospective cohort, registry, claims data
electronic health record, ehr, emr, administrative data
pharmacovigilance, drug safety, adverse event, adverse drug, safety signal
propensity score, instrumental variable, target trial, causal inference
cohort study, case-control, self-controlled, new user
comparative effectiveness, post-marketing"""

# ========================================
# Streamlit Secrets Configuration
# ========================================
# OLLAMA_API_KEY = "your_ollama_cloud_api_key"
# OLLAMA_MODEL = "gptoss-120b:cloud"
# Get your API key from: https://ollama.com/settings/keys
# ========================================

st.set_page_config(
    page_title="Medical Literature Trends",
    page_icon="📊",
    layout="wide"
)


def get_secret(key: str, default: str = "") -> str:
    """Safely retrieve secrets with fallback to environment variables."""
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


def generate_html_report(journals_data, trend_analysis, journal_names):
    """Generate HTML report for download."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medical Literature Trend Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6; 
            color: #333; 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f8f9fa;
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 30px; 
            border-radius: 12px; 
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .meta {{ color: rgba(255,255,255,0.9); font-size: 0.95em; }}
        .section {{ 
            background: white; 
            padding: 25px; 
            margin-bottom: 20px; 
            border-radius: 12px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        .section h2 {{ 
            color: #667eea; 
            border-bottom: 2px solid #eee; 
            padding-bottom: 10px; 
            margin-bottom: 20px; 
        }}
        .trend-analysis {{ 
            background: #f0f4ff; 
            padding: 20px; 
            border-radius: 8px; 
            border-left: 4px solid #667eea;
        }}
        .trend-analysis h3 {{ color: #4a5568; margin-top: 15px; margin-bottom: 8px; }}
        .journal {{ margin-bottom: 25px; }}
        .journal-title {{ 
            font-size: 1.2em; 
            color: #2d3748; 
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .paper {{ 
            border: 1px solid #e2e8f0; 
            padding: 15px; 
            margin-bottom: 12px; 
            border-radius: 8px;
            transition: box-shadow 0.2s;
        }}
        .paper:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .paper-title {{ 
            font-weight: 600; 
            color: #2d3748; 
            margin-bottom: 8px;
            font-size: 1.05em;
        }}
        .paper-title a {{ color: #667eea; text-decoration: none; }}
        .paper-title a:hover {{ text-decoration: underline; }}
        .paper-meta {{ color: #718096; font-size: 0.9em; margin-bottom: 10px; }}
        .paper-abstract {{ 
            font-size: 0.95em; 
            color: #4a5568; 
            background: #f7fafc; 
            padding: 12px;
            border-radius: 6px;
        }}
        .footer {{ 
            text-align: center; 
            color: #a0aec0; 
            padding: 20px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Medical Literature Trend Report</h1>
        <div class="meta">
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Journals:</strong> {', '.join(journal_names)}</p>
        </div>
    </div>
"""
    
    # Trend Analysis Section
    if trend_analysis:
        # Convert markdown-style formatting to HTML
        trend_html = trend_analysis.replace('### ', '<h3>').replace('\n\n', '</p><p>')
        trend_html = trend_html.replace('**', '<strong>').replace('**', '</strong>')
        trend_html = f"<p>{trend_html}</p>"
        
        html += f"""
    <div class="section">
        <h2>🔬 AI Trend Analysis</h2>
        <div class="trend-analysis">
            {trend_html}
        </div>
    </div>
"""
    
    # Papers Section
    total_papers = sum(len(papers) for papers in journals_data.values())
    html += f"""
    <div class="section">
        <h2>📚 Recent Papers ({total_papers} total)</h2>
"""
    
    for journal_name, papers in journals_data.items():
        html += f"""
        <div class="journal">
            <div class="journal-title">📖 {journal_name} ({len(papers)} papers)</div>
"""
        for i, paper in enumerate(papers, 1):
            abstract = paper.get('abstract', '')[:400]
            if len(paper.get('abstract', '')) > 400:
                abstract += '...'
            
            html += f"""
            <div class="paper">
                <div class="paper-title">{i}. <a href="{paper['link']}" target="_blank">{paper['title']}</a></div>
                <div class="paper-meta">📅 {paper.get('published', 'Unknown date')}</div>
                <div class="paper-abstract">{abstract}</div>
            </div>
"""
        html += "        </div>\n"
    
    html += """
    </div>
    <div class="footer">
        <p>Generated by Medical Literature Trend Analyzer</p>
    </div>
</body>
</html>"""
    
    return html


def main():
    st.title("📊 Medical Literature Trend Analyzer")
    st.markdown("Analyze research trends from top medical journals using AI.")

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
        
        # Max papers per journal
        max_papers = st.slider(
            "Max Papers per Journal",
            min_value=5,
            max_value=30,
            value=10,
            help="Limit to the most recent N papers per journal"
        )
        
        st.divider()
        
        # RWD/Pharmacoepi Filter
        st.subheader("🔬 Focus Filter")
        enable_focus_filter = st.checkbox(
            "Enable RWD/Pharmacoepi Focus",
            value=True,
            help="Also analyze RWD/Pharmacoepi papers separately"
        )
        
        if enable_focus_filter:
            # Editable keywords
            filter_keywords = st.text_area(
                "Filter Keywords (one per line or comma-separated)",
                value=DEFAULT_RWD_KEYWORDS,
                height=150,
                help="Edit keywords to filter papers. Papers matching any keyword will be included."
            )
        else:
            filter_keywords = ""
        
        st.divider()
        
        # API Key Status
        ollama_api_key = get_secret("OLLAMA_API_KEY", "")
        
        st.subheader("📋 Status")
        if ollama_api_key:
            st.success("✅ Ollama API Key Configured")
        else:
            st.warning("⚠️ No API Key (Trend analysis disabled)")
            st.caption("[Get key](https://ollama.com/settings/keys)")

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
        help="Select multiple journals to analyze"
    )
    
    if not selected_journal_names:
        st.warning("⚠️ Please select at least one journal")
        st.stop()
    
    selected_journals = [j for j in JOURNALS if j["name"] in selected_journal_names]

    # Fetch Papers Button
    if st.button("🔍 Fetch Papers & Analyze Trends", type="primary", use_container_width=True):
        # Initialize collector
        collector = PaperCollector()
        
        # Fetch papers from all selected journals
        all_papers = []
        
        with st.status(f"Fetching papers from {len(selected_journals)} journal(s)...", expanded=True) as status:
            for journal in selected_journals:
                status.write(f"📡 Fetching from {journal['name']}...")
                papers = collector.fetch_papers(journal["url"], months_back, max_papers)
                
                # Add source journal to each paper
                for paper in papers:
                    paper['source'] = journal['name']
                    paper['category'] = journal.get('category', 'Other')
                    all_papers.append(paper)
                
                status.write(f"✅ Found {len(papers)} papers from {journal['name']}")
            
            if not all_papers:
                status.update(label="No papers found", state="error")
                st.error("No papers found. Try a different time period or check journal availability.")
                st.stop()
            
            status.update(label=f"✅ Fetched {len(all_papers)} papers!", state="complete", expanded=False)
        
        # Apply RWD/Pharmacoepi filter for focused analysis
        filtered_papers = []
        if enable_focus_filter and filter_keywords:
            # Parse keywords from text area
            keywords = []
            for line in filter_keywords.split('\n'):
                for kw in line.split(','):
                    kw = kw.strip().lower()
                    if kw:
                        keywords.append(kw)
            
            # Filter papers
            for paper in all_papers:
                text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
                if any(kw in text for kw in keywords):
                    filtered_papers.append(paper)
        
        # Store papers in session state
        st.session_state['all_papers'] = all_papers
        st.session_state['filtered_papers'] = filtered_papers
        st.session_state['selected_journals'] = selected_journal_names
        st.session_state['filter_enabled'] = enable_focus_filter and len(filtered_papers) > 0
        
        # AI Trend Analysis (both all and filtered)
        if ollama_api_key:
            analyzer = TrendAnalyzer(api_key=ollama_api_key, model=model_name)
            
            # Always analyze all papers
            with st.spinner("🤖 Analyzing all papers trend..."):
                trend_all = analyzer.analyze_trends(all_papers)
                st.session_state['trend_all'] = trend_all
            
            # Analyze filtered papers if available
            if filtered_papers:
                with st.spinner(f"🔬 Analyzing RWD/Pharmacoepi focus ({len(filtered_papers)} papers)..."):
                    trend_filtered = analyzer.analyze_trends(filtered_papers)
                    st.session_state['trend_filtered'] = trend_filtered
            else:
                st.session_state['trend_filtered'] = None
        else:
            st.session_state['trend_all'] = None
            st.session_state['trend_filtered'] = None

    # Display results
    if 'all_papers' in st.session_state:
        all_papers = st.session_state['all_papers']
        filtered_papers = st.session_state.get('filtered_papers', [])
        filter_enabled = st.session_state.get('filter_enabled', False)
        
        # Summary stats
        st.info(f"📊 **Total**: {len(all_papers)} papers | **RWD/Pharmacoepi Match**: {len(filtered_papers)} papers")
        
        # Create two columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(f"📚 Paper List ({len(all_papers)})")
            
            # Group by journal
            journals_data = {}
            for paper in all_papers:
                source = paper['source']
                if source not in journals_data:
                    journals_data[source] = []
                journals_data[source].append(paper)
            
            # Store for download
            st.session_state['journals_data'] = journals_data
            
            # Display papers grouped by journal
            for journal_name, journal_papers in journals_data.items():
                with st.expander(f"📖 {journal_name} ({len(journal_papers)} papers)", expanded=True):
                    for i, paper in enumerate(journal_papers, 1):
                        # Highlight if matched filter
                        is_filtered = paper in filtered_papers
                        prefix = "🔬 " if is_filtered else ""
                        st.markdown(f"**{prefix}{i}. [{paper['title']}]({paper['link']})**")
                        st.caption(f"📅 {paper.get('published', 'Unknown date')}")
                        
                        # Show abstract
                        abstract = paper.get('abstract', '')
                        if abstract and abstract != "No abstract available":
                            st.markdown(f"<small>{abstract[:300]}...</small>", unsafe_allow_html=True)
                        st.divider()
        
        with col2:
            st.subheader("🔬 AI Trend Analysis")
            
            # Create tabs for dual analysis
            if filter_enabled:
                tab1, tab2 = st.tabs(["📊 All Papers", "🔬 RWD/Pharmacoepi Focus"])
                
                with tab1:
                    if st.session_state.get('trend_all'):
                        st.markdown(st.session_state['trend_all'])
                    else:
                        st.warning("⚠️ No trend analysis available")
                
                with tab2:
                    st.caption(f"*Based on {len(filtered_papers)} matching papers*")
                    if st.session_state.get('trend_filtered'):
                        st.markdown(st.session_state['trend_filtered'])
                    else:
                        st.warning("⚠️ No filtered papers trend analysis")
            else:
                # Only all papers analysis
                if st.session_state.get('trend_all'):
                    st.markdown(st.session_state['trend_all'])
                elif not get_secret("OLLAMA_API_KEY"):
                    st.warning("⚠️ Add OLLAMA_API_KEY to enable AI trend analysis")
                else:
                    st.info("Click 'Fetch Papers & Analyze Trends' to generate analysis")
        
        # Download section
        st.divider()
        st.subheader("📥 Download Report")
        
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            # Download HTML Report
            html_report = generate_html_report(
                journals_data, 
                st.session_state.get('trend_all', ''),
                st.session_state.get('selected_journals', [])
            )
            st.download_button(
                label="🌐 Download HTML Report",
                data=html_report,
                file_name=f"trend_report_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )
        
        with col_dl2:
            # Download Markdown (for developers)
            if st.session_state.get('trend_all'):
                md_report = generate_markdown_report(
                    journals_data, 
                    st.session_state['trend_all'],
                    st.session_state.get('selected_journals', [])
                )
                st.download_button(
                    label="📄 Download Markdown",
                    data=md_report,
                    file_name=f"trend_report_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )


def generate_markdown_report(journals_data, trend_analysis, journal_names):
    """Generate markdown report."""
    md = f"# Medical Literature Trend Report\n"
    md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    md += f"**Journals:** {', '.join(journal_names)}\n\n"
    md += "---\n\n"
    
    md += "## 🔬 AI Trend Analysis\n\n"
    md += trend_analysis + "\n\n"
    md += "---\n\n"
    
    md += "## 📚 Paper List\n\n"
    
    for journal_name, papers in journals_data.items():
        md += f"### {journal_name} ({len(papers)} papers)\n\n"
        for i, paper in enumerate(papers, 1):
            md += f"{i}. [{paper['title']}]({paper['link']})\n"
            md += f"   - Published: {paper.get('published', 'Unknown')}\n\n"
    
    return md


if __name__ == "__main__":
    main()
