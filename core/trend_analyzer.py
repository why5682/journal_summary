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

    def __init__(self, model_name="gpt-oss:120b"):
        import os
        import streamlit as st
        
        self.model = model_name
        self.api_key = os.environ.get("OLLAMA_API_KEY")
        
        # Try loading from secrets if not in env
        if not self.api_key:
            try:
                self.api_key = st.secrets.get("OLLAMA_API_KEY", "")
            except:
                self.api_key = ""
                
        # Initialize Client based on API Key presence (Cloud vs Local)
        if self.api_key:
            # Cloud Mode
            self.client = Client(
                host="https://ollama.com",
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            if model_name == "gptoss-120b:cloud": 
                self.model = "gpt-oss:120b"
        else:
            # Local Mode
            self.client = Client(host='http://localhost:11434')
            
        logger.info(f"Initialized Trend Analyzer with model: {self.model}")

    def analyze_trends(self, papers: List[Dict[str, Any]], language: str = "en") -> str:
        """
        Analyze trends across all papers.
        
        Args:
            papers: List of paper dictionaries with title, abstract, source
            language: Response language ('en' for English, 'ko' for Korean)
            
        Returns:
            AI-generated trend analysis
        """
        if not papers:
            return "No papers to analyze." if language == "en" else "분석할 논문이 없습니다."
        
        # Build paper list for prompt
        paper_list = self._build_paper_list(papers)
        prompt = self._build_trend_prompt(paper_list, len(papers), language)
        
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

    def _build_trend_prompt(self, paper_list: str, paper_count: int, language: str = "en") -> str:
        """Build the trend analysis prompt."""
        
        if language == "ko":
            lang_instruction = "반드시 한국어로 답변하세요. 의학 용어는 영어 병기 가능."
        else:
            lang_instruction = "Respond in English."
        
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

{lang_instruction} Be concise but insightful. Focus on patterns across multiple papers, not individual paper summaries."""
