# 📚 Top Medical Journals Summarizer

AI-powered tool to fetch and summarize the latest research papers from top medical journals (BMJ, The Lancet, NEJM).

## 🌟 Features

- 📰 **RSS Feed Integration**: Automatically fetch latest papers from:
  - The BMJ
  - The Lancet
  - NEJM
- 🤖 **AI Summarization**: Get concise, professional summaries using Ollama Cloud
- 📥 **Download Reports**: Export summaries as Markdown files
- ⚙️ **Customizable**: Choose number of papers and model
- 🔐 **Secure**: API key management via Streamlit Secrets

---

## 🚀 Quick Start

### **Deploy to Streamlit Cloud**

**Step 1: Get Ollama Cloud API Key**
1. Sign up at [ollama.com](https://ollama.com)
2. Go to [API Keys](https://ollama.com/settings/keys)
3. Create a new API key

**Step 2: Push to GitHub**
```bash
cd Ollama_Medical_Bot

# Add deployment files
git add app.py requirements.txt .streamlit/secrets.toml.example README.md .gitignore
git commit -m "📚 Deploy Medical Journals Summarizer"
git push origin main
```

**Step 3: Deploy**
1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Create new app → Select your repository
3. Main file: `app.py`
4. Deploy!

**Step 4: Configure Secrets**
In Streamlit Cloud dashboard → Settings → Secrets:
```toml
OLLAMA_MODEL = "gptoss-120b:cloud"
OLLAMA_API_KEY = "your_actual_api_key"
```

---

## 📋 How It Works

1. **Select Journal**: Choose from BMJ, Lancet, or NEJM
2. **Set Parameters**: Number of papers to fetch (1-20)
3. **Fetch & Summarize**: Click button to:
   - Fetch latest papers from RSS feed
   - Get AI-powered summary for each paper
   - Display results with links
4. **Download**: Export all summaries as Markdown report

---

## 📊 Summary Format

Each paper summary includes:
- **Main Objective**: Research goal
- **Key Findings**: Important results
- **Clinical Significance**: Practical implications

Perfect for busy clinicians who need quick insights!

---

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OLLAMA_API_KEY=your_key
export OLLAMA_MODEL=gptoss-120b:cloud

# Run app
streamlit run app.py
```

---

## 📦 Project Structure

```
Ollama_Medical_Bot/
├── app.py                          # Main Streamlit app
├── requirements.txt                # Dependencies
├── .gitignore                      # Git ignore rules
├── .streamlit/
│   └── secrets.toml.example        # Secrets template
└── README.md                       # This file
```

---

## 🎯 Supported Journals

| Journal | RSS Feed |
|---------|----------|
| **The BMJ** | Latest research articles |
| **The Lancet** | Current issue articles |
| **NEJM** | New England Journal of Medicine |

---

## 🐛 Troubleshooting

### No Papers Found
- RSS feed may be temporarily unavailable
- Try different journal
- Check internet connection

### Summarization Errors
- Verify Ollama API key
- Check model availability
- Try reducing number of papers

### Download Issues
- Browser may block downloads
- Allow downloads in browser settings

---

## 💡 Tips

- **Start Small**: Try 5 papers first to test
- **Save Reports**: Download regularly for your records
- **Model Selection**: Experiment with different Ollama models
- **Batch Processing**: Can process up to 20 papers at once

---

## 🔒 Security

- API keys stored securely in Streamlit Secrets
- No data stored on server
- Summaries generated on-demand

---

**Built with ❤️ for Medical Professionals**
