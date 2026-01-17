# Medical Literature Summarizer

AI-powered medical paper summarization tool using Streamlit and Ollama Cloud.

## Features

- 📰 **Multi-Journal Support** - Fetch papers from top medical journals
- 🤖 **AI Summarization** - Concise summaries using Ollama Cloud
- 🔄 **Duplicate Detection** - Skip already processed papers
- 📥 **Export Reports** - Download summaries as Markdown

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add your API key:

```toml
OLLAMA_API_KEY = "your_api_key_here"
OLLAMA_MODEL = "gptoss-120b:cloud"
```

Get your API key from: https://ollama.com/settings/keys

### 3. Run the App

```bash
streamlit run app.py
```

## Supported Journals

### Pharmacoepidemiology
- Pharmacoepidemiology and Drug Safety
- Drug Safety

### Clinical Pharmacology
- Clinical Pharmacology & Therapeutics
- British Journal of Clinical Pharmacology

### General Medical
- NEJM, The Lancet, JAMA, The BMJ, Annals of Internal Medicine

## Project Structure

```
medical_summarizer/
├── app.py              # Streamlit main app
├── core/
│   ├── collector.py    # RSS feed collection
│   ├── summarizer.py   # Ollama Cloud integration
│   └── storage.py      # SQLite duplicate tracking
├── config/
│   └── journals.py     # Journal definitions
└── .streamlit/
    └── secrets.toml    # API configuration
```
