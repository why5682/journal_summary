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

    def __init__(
        self, 
        api_key: str,
        model: str = "gptoss-120b:cloud",
        host: str = "https://ollama.com"
    ):
        """
        Initialize the summarizer with Ollama Cloud credentials.
        
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
        logger.info(f"Initialized Ollama Cloud summarizer with model: {model}")

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
