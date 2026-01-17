# 📊 Medical Literature Trend Analyzer

AI-powered tool to analyze research trends from top medical journals.

## 🌟 Features

- 📰 **Multi-Journal Support** - Fetch from 7 major journals
- 🔬 **AI Trend Analysis** - Identify research patterns using Ollama Cloud
- 🌐 **HTML Export** - Beautiful, accessible reports
- 📄 **Markdown Export** - Developer-friendly format

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# .streamlit/secrets.toml
OLLAMA_API_KEY = "your_api_key_here"
OLLAMA_MODEL = "gptoss-120b:cloud"
```

### 3. Run
```bash
streamlit run app.py
```

## 📚 Supported Journals

| Category | Journals |
|----------|----------|
| **Pharmacoepidemiology** | PDS, Drug Safety |
| **Clinical Pharmacology** | CPT, BJCP |
| **General Medical** | NEJM, Lancet, JAMA |

## 🏗️ Project Structure

```
medical_summarizer/
├── app.py              # Streamlit app
├── core/
│   ├── collector.py    # RSS collection
│   ├── trend_analyzer.py  # AI analysis
│   └── storage.py      # SQLite storage
├── config/
│   └── journals.py     # Journal definitions
└── requirements.txt
```

## 🔐 Deployment

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from repo
4. Add secrets in Settings → Secrets
