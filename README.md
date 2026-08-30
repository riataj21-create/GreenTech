# 🌿 GreenTech — AI Farmer Advisory System

A multilingual AI-powered agricultural advisory app for the farmers.

---

## ✨ Features

- 🤖 **AI Advice** — Powered by OpenRouter / Google Gemini
- 🌐 **5 Languages** — English, Telugu, Hindi, Tamil, Kannada
- 🎤 **Voice Input** — Speak your crop problem (Faster-Whisper)
- 🔊 **Read Aloud** — AI advice spoken back to you
- 🌤️ **Live Weather** — Real-time  weather with farming tips
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


### 4. Run the app
```bash
streamlit run main.py
```

Open **http://localhost:8501** in your browser.


---

## 🌾 Built For

Especially all the Farmers — providing AI-powered crop advice in local languages.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI**: OpenRouter (free) / Google Gemini
- **Voice**: Faster-Whisper (speech-to-text)
- **TTS**: Windows SAPI (text-to-speech)
- **Weather**: OpenWeatherMap API
