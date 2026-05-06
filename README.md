# VOXIS — AI Voice Studio

> **Transform Voice · Transcribe Speech · Synthesise Sound**  
> Powered by [Azure Cognitive Services](https://azure.microsoft.com/en-us/products/ai-services/ai-speech) · Built with [Streamlit](https://streamlit.io)

---

## ✦ Features

| Feature | Details |
|---|---|
| **Speech → Text** | Upload WAV / MP3 / OGG / FLAC / M4A and get a full transcript |
| **Text → Speech** | Type any text (up to 3,000 chars) and download studio-quality WAV |
| **8 Neural Voices** | Jenny, Aria, Emma, Guy, Davis, Brian, Sonia, Ryan |
| **10+ Languages** | English (US/UK/IN), Hindi, Spanish, French, German, Portuguese, Japanese, Mandarin |
| **Export Options** | Download transcripts as `.txt` or `.json`, audio as `.wav` |
| **Secure Credentials** | Credentials loaded exclusively from `st.secrets` — never hardcoded |

---

## ⚡ Quick Start (Local)

### 1. Clone the repository

```bash
git clone https://github.com/Ankit-Tank/voxis.git
cd voxis
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure credentials

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Open `.streamlit/secrets.toml` and fill in your real Azure credentials:

```toml
AZURE_SPEECH_KEY    = "your-azure-speech-key-here"
AZURE_SPEECH_REGION = "eastus"
```

> ⚠️ `.streamlit/secrets.toml` is gitignored. Never commit it.

### 5. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ☁️ Deploy on Streamlit Cloud

1. **Push this repository to GitHub** (make sure `secrets.toml` is NOT included — it is gitignored by default).

2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → select your repo.

3. Set the main file path to `app.py`.

4. Click **Advanced settings → Secrets** and paste:

```toml
AZURE_SPEECH_KEY    = "your-azure-speech-key-here"
AZURE_SPEECH_REGION = "eastus"
```

5. Click **Deploy**. Your credentials are stored securely in Streamlit's encrypted secret store — they are never exposed to end users or visible in the source code.

---

## 🔑 Getting Azure Credentials

1. Sign in to the [Azure Portal](https://portal.azure.com).
2. Create a resource: **Azure AI services → Speech service**.
3. Choose a region (e.g. `eastus`, `centralindia`).
4. After deployment, navigate to **Keys and Endpoint**.
5. Copy **KEY 1** → paste as `AZURE_SPEECH_KEY`.
6. Copy the **Location/Region** value → paste as `AZURE_SPEECH_REGION`.

> The free tier (F0) provides 5 hours of speech recognition and 0.5 million TTS characters per month at no cost.

---

## 📁 Project Structure

```
voxis/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .gitignore                      # Excludes secrets & temp files
├── README.md                       # This file
└── .streamlit/
    ├── config.toml                 # Streamlit theme & server config
    └── secrets.toml.example        
```

---

## 🔒 Security Model

| Layer | How credentials are protected |
|---|---|
| **Local dev** | Stored in `.streamlit/secrets.toml`, excluded from Git via `.gitignore` |
| **Streamlit Cloud** | Stored in the platform's encrypted secret store, injected at runtime via `st.secrets` |
| **Source code** | Zero credentials in `app.py` or any committed file |
| **Public users** | Access only the UI; the app server holds the key and calls Azure on their behalf |

---

## 🛠 Supported Audio Formats

| Format | Extension | Notes |
|---|---|---|
| WAV | `.wav` | Best quality, recommended |
| MP3 | `.mp3` | Widely supported |
| OGG | `.ogg` | Open source format |
| FLAC | `.flac` | Lossless |
| M4A / MP4 | `.m4a`, `.mp4` | Apple / AAC format |

---

## 📜 License

MIT — see [LICENSE](LICENSE) for details.
