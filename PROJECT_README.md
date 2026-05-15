# Sunbird AI Pipeline

## Project Description
A Streamlit web application that accepts text or audio input and runs it through a full AI pipeline powered by the Sunbird AI API. The app transcribes audio, summarises the content, translates the summary into a chosen Ugandan local language, and generates a spoken audio clip of the translation — all shown step by step in the UI.

## Architecture Overview

User input (text or audio)
│
▼
[1] STT — POST /tasks/stt                  (audio only)
│  Sunbird Speech-to-Text API
▼
[2] Summarise — POST /tasks/sunflower_inference
│  Sunflower LLM
▼
[3] Translate — POST /tasks/sunflower_inference
│  Sunflower LLM
▼
[4] TTS — POST /tasks/tts
│  Sunbird Text-to-Speech API
▼
Output displayed in Streamlit UI

## Local Setup

```bash
git clone https://github.com/<your-github-username>/internship-assessment.git
cd internship-assessment
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
cp .env.example .env
# Open .env and add your Sunbird API token
streamlit run app.py
```

## Environment Variables

| Variable | Description |
|---|---|
| `SUNBIRD_API_TOKEN` | Your Sunbird AI API bearer token. Get it from https://api.sunbird.ai |

## Usage

1. Open the app
2. Choose **Text** or **Audio file** as input
3. Paste text or upload an audio file (max 5 minutes)
4. Pick a target language (Luganda, Runyankole, Ateso, Lugbara, Acholi)
5. Click **▶ Run pipeline**
6. View the transcript, summary, translation and play the generated audio

## Deployed Link

https://huggingface.co/spaces/FaithKirabo256/sunbird-ai-pipeline

## Known Limitations

- Audio files longer than 5 minutes are rejected
- TTS is only available for the 5 supported Ugandan languages
- The Sunbird API can sometimes be slow and time out — retry if this happens
- Large audio files above 100MB are not supported