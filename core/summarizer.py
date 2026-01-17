"""
Paper Summarizer Module
Uses Ollama Cloud API for AI-powered paper summarization.
"""
import logging
from typing import Optional
from ollama import Client

logger = logging.getLogger(__name__)


class PaperSummarizer:
    """Handles paper summarization using Ollama Cloud API."""

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
            # Legacy mapping
            if model_name == "gptoss-120b:cloud": 
                self.model = "gpt-oss:120b"
        else:
            # Local Mode
            self.client = Client(host='http://localhost:11434')
            
        logger.info(f"Initialized Summarizer with model: {self.model}")

    def summarize(self, title: str, abstract: str) -> str:
        """
        Summarize a paper given its title and abstract.
        
        Args:
            title: Paper title
            abstract: Paper abstract
            
        Returns:
            AI-generated summary string
        """
        prompt = self._build_prompt(title, abstract)
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return f"⚠️ Summarization failed: {str(e)}"

    def _build_prompt(self, title: str, abstract: str) -> str:
        """Build the summarization prompt."""
        return f"""You are an expert medical researcher. Summarize the following research paper in a concise, professional manner.

Title: {title}

Abstract: {abstract}

Provide a summary that includes:
1. **Objective**: Main research goal
2. **Key Findings**: Most important results
3. **Clinical Significance**: Practical implications

Keep it to 3-4 sentences, suitable for busy clinicians. Respond in English only."""
