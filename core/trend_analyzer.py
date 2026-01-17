"""
Trend Analyzer Module
Analyzes trends across multiple papers using Ollama Cloud.
"""
import logging
from typing import List, Dict, Any
from ollama import Client

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analyzes trends across a collection of papers."""

    def __init__(
        self, 
        api_key: str,
        model: str = "gptoss-120b:cloud",
        host: str = "https://ollama.com"
    ):
        """
        Initialize the trend analyzer with Ollama Cloud credentials.
        
        Args:
            api_key: Ollama Cloud API key
            model: Model name to use
            host: Ollama Cloud host URL
        """
        self.model = model
        self.client = Client(
            host=host,
            headers={'Authorization': f'Bearer {api_key}'}
        )
        logger.info(f"Initialized Trend Analyzer with model: {model}")

    def analyze_trends(self, papers: List[Dict[str, Any]]) -> str:
        """
        Analyze trends across all papers.
        
        Args:
            papers: List of paper dictionaries with title, abstract, source
            
        Returns:
            AI-generated trend analysis
        """
        if not papers:
            return "No papers to analyze."
        
        # Build paper list for prompt
        paper_list = self._build_paper_list(papers)
        prompt = self._build_trend_prompt(paper_list, len(papers))
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return f"⚠️ Trend analysis failed: {str(e)}"

    def _build_paper_list(self, papers: List[Dict[str, Any]]) -> str:
        """Build formatted paper list for the prompt."""
        lines = []
        for i, paper in enumerate(papers, 1):
            source = paper.get('source', 'Unknown')
            title = paper.get('title', 'Untitled')
            abstract = paper.get('abstract', '')[:500]  # Limit abstract length
            lines.append(f"{i}. [{source}] {title}")
            if abstract:
                lines.append(f"   Abstract: {abstract}...")
            lines.append("")
        return "\n".join(lines)

    def _build_trend_prompt(self, paper_list: str, paper_count: int) -> str:
        """Build the trend analysis prompt."""
        return f"""You are an expert pharmacoepidemiologist and medical researcher. Analyze the following {paper_count} recent papers from top medical journals and identify key research trends.

## Recent Papers:
{paper_list}

## Your Task:
Provide a comprehensive trend analysis in the following format:

### 🔬 Key Research Trends (Top 3-5)
Identify the most prominent research themes or topics emerging from these papers.

### 💊 Drug/Therapeutic Focus
List any specific drugs, drug classes, or therapeutic areas that appear frequently.

### 📊 Methodological Patterns
Note any common study designs, data sources, or analytical approaches.

### 🎯 Clinical Implications
Summarize the potential impact on clinical practice or drug safety.

### 📈 Emerging Topics
Highlight any novel or emerging areas of research.

Respond in English. Be concise but insightful. Focus on patterns across multiple papers, not individual paper summaries."""
