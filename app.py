"""
Medical Literature Summarizer
Streamlit app for AI-powered trend analysis of medical research.
"""
import streamlit as st
from datetime import datetime
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import PaperCollector, TrendAnalyzer
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
                st.error("No papers found. Try a different time period.")
                st.stop()
            
            status.update(label=f"✅ Fetched {len(all_papers)} papers!", state="complete", expanded=False)
        
        # Store papers in session state
        st.session_state['papers'] = all_papers
        st.session_state['selected_journals'] = selected_journal_names
        
        # AI Trend Analysis
        if ollama_api_key:
            with st.spinner("🤖 Analyzing trends with AI..."):
                analyzer = TrendAnalyzer(api_key=ollama_api_key, model=model_name)
                trend_analysis = analyzer.analyze_trends(all_papers)
                st.session_state['trend_analysis'] = trend_analysis
        else:
            st.session_state['trend_analysis'] = None

    # Display results
    if 'papers' in st.session_state:
        papers = st.session_state['papers']
        
        # Create two columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(f"📚 Recent Papers ({len(papers)})")
            
            # Group by journal
            journals_data = {}
            for paper in papers:
                source = paper['source']
                if source not in journals_data:
                    journals_data[source] = []
                journals_data[source].append(paper)
            
            # Display papers grouped by journal
            for journal_name, journal_papers in journals_data.items():
                with st.expander(f"📖 {journal_name} ({len(journal_papers)} papers)", expanded=True):
                    for i, paper in enumerate(journal_papers, 1):
                        st.markdown(f"**{i}. [{paper['title']}]({paper['link']})**")
                        st.caption(f"📅 {paper.get('published', 'Unknown date')}")
                        
                        # Show abstract in a smaller text
                        abstract = paper.get('abstract', '')
                        if abstract and abstract != "No abstract available":
                            with st.container():
                                st.markdown(f"<small>{abstract[:300]}...</small>", unsafe_allow_html=True)
                        st.divider()
        
        with col2:
            st.subheader("🔬 AI Trend Analysis")
            
            if st.session_state.get('trend_analysis'):
                st.markdown(st.session_state['trend_analysis'])
            elif not ollama_api_key:
                st.warning("⚠️ Add OLLAMA_API_KEY to enable AI trend analysis")
            else:
                st.info("Click 'Fetch Papers & Analyze Trends' to generate analysis")
        
        # Download section
        st.divider()
        st.subheader("📥 Download Report")
        
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            # Download paper list
            paper_md = generate_paper_list_markdown(journals_data)
            st.download_button(
                label="📄 Paper List (Markdown)",
                data=paper_md,
                file_name=f"papers_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col_dl2:
            # Download full report with trend analysis
            if st.session_state.get('trend_analysis'):
                full_md = generate_full_report(
                    journals_data, 
                    st.session_state['trend_analysis'],
                    st.session_state.get('selected_journals', [])
                )
                st.download_button(
                    label="📊 Full Report with Trends",
                    data=full_md,
                    file_name=f"trend_report_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )


def generate_paper_list_markdown(journals_data):
    """Generate markdown list of papers."""
    md = f"# Medical Literature - Paper List\n"
    md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md += "---\n\n"
    
    for journal_name, papers in journals_data.items():
        md += f"## {journal_name}\n\n"
        for i, paper in enumerate(papers, 1):
            md += f"### {i}. {paper['title']}\n\n"
            md += f"**Published:** {paper.get('published', 'Unknown')}\n\n"
            md += f"**Abstract:** {paper.get('abstract', 'N/A')}\n\n"
            md += f"[Read Full Paper]({paper['link']})\n\n"
            md += "---\n\n"
    
    return md


def generate_full_report(journals_data, trend_analysis, journal_names):
    """Generate full report with papers and trend analysis."""
    md = f"# Medical Literature Trend Report\n"
    md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    md += f"**Journals:** {', '.join(journal_names)}\n\n"
    md += "---\n\n"
    
    # Trend Analysis Section
    md += "## 🔬 AI Trend Analysis\n\n"
    md += trend_analysis + "\n\n"
    md += "---\n\n"
    
    # Paper List Section
    md += "## 📚 Paper List\n\n"
    
    total_papers = sum(len(papers) for papers in journals_data.values())
    md += f"*Total: {total_papers} papers*\n\n"
    
    for journal_name, papers in journals_data.items():
        md += f"### {journal_name} ({len(papers)} papers)\n\n"
        for i, paper in enumerate(papers, 1):
            md += f"{i}. [{paper['title']}]({paper['link']})\n"
            md += f"   - Published: {paper.get('published', 'Unknown')}\n\n"
    
    return md


if __name__ == "__main__":
    main()
