# 🌱 GreenTech — AI Farmer Advisory System

A multilingual AI-powered agricultural advisory system that helps farmers understand crop problems and receive practical guidance in their preferred language.

## ✨ Features

- 🤖 **AI Agricultural Advice** — AI-powered analysis of crop problems
- 🌐 **5 Languages** — English, Telugu, Hindi, Tamil, Kannada
- 🎤 **Voice Input** — Speak your crop problem using speech-to-text
- 🖼️ **Image Input** — Upload a crop image for analysis
- 🔊 **Read Aloud** — Listen to the generated advice
- 🌤️ **Live Weather** — Weather information with farming guidance
- 📋 **History** — View previous queries and advice

## 🛠️ Technology

- **Frontend:** Streamlit
- **AI:** OpenRouter
- **Speech-to-Text:** Faster-Whisper
- **Text-to-Speech:** Windows SAPI
- **Weather:** OpenWeatherMap API

## 🚀 Run Locally

```bash
git clone https://github.com/riataj21-create/GreenTech.git
cd GreenTech
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run main.py
