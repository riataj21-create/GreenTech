# 🌿 GreenTech — AI Farmer Advisory System

A multilingual AI-powered agricultural advisory app for Indian farmers, built for the **Madanapalle** region, Andhra Pradesh.

---

## ✨ Features

- 🤖 **AI Advice** — Powered by OpenRouter / Google Gemini
- 🌐 **5 Languages** — English, Telugu, Hindi, Tamil, Kannada
- 🎤 **Voice Input** — Speak your crop problem (Faster-Whisper)
- 🔊 **Read Aloud** — AI advice spoken back to you
- 🌤️ **Live Weather** — Real-time Madanapalle weather with farming tips
- 📋 **History** — All past queries saved and searchable

---

## 🚀 Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/GreenTech.git
cd GreenTech
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API keys
```bash
copy .env.example .env
# Open .env and fill in your keys
```

### 5. Run the app
```bash
streamlit run main.py
```

Open **http://localhost:8501** in your browser.

---

## 🔑 API Keys Needed

| Key | Where to get it | Free? |
|-----|----------------|-------|
| `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai) | ✅ Free tier |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/apikey) | ✅ Free tier |
| `WEATHER_API_KEY` | [openweathermap.org](https://openweathermap.org/api) | ✅ Free tier |

---

## 🌾 Built For

Farmers in **Madanapalle, Andhra Pradesh** — providing AI-powered crop advice in local languages.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI**: OpenRouter (free) / Google Gemini
- **Voice**: Faster-Whisper (speech-to-text)
- **TTS**: Windows SAPI (text-to-speech)
- **Weather**: OpenWeatherMap API
