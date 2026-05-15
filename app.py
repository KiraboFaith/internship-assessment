import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from backend.pipeline import run_pipeline

st.set_page_config(
    page_title="Sunbird AI Pipeline",
    page_icon="🌻",
    layout="centered",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'DM Serif Display', serif; }
    .result-box {
        background: #fffbf0;
        color: #111111;
        border-left: 4px solid #e8a020;
        border-radius: 6px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        white-space: pre-wrap;
    }
    .step-label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #e8a020;
        margin-bottom: 0.25rem;
    }
    .stButton > button {
        background: #e8a020;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.55rem 1.8rem;
    }
    .stButton > button:hover { background: #c98a18; color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌻 Sunbird AI Pipeline")
st.caption("Text or audio → Transcribe → Summarise → Translate → Hear it spoken")
st.divider()

col1, col2 = st.columns([1, 1])
with col1:
    input_type = st.radio("Input type", options=["Text", "Audio file"], horizontal=True)
with col2:
    target_language = st.selectbox(
        "Target language",
        options=["Luganda", "Runyankole", "Ateso", "Lugbara", "Acholi"],
    )

st.write("")

text_input = None
audio_path = None

if input_type == "Text":
    text_input = st.text_area(
        "Paste or type your text here",
        height=200,
        placeholder="Enter any text you'd like summarised and translated…",
    )
else:
    uploaded = st.file_uploader(
        "Upload an audio file (MP3, WAV, OGG, M4A, AAC — max 5 min)",
        type=["mp3", "wav", "ogg", "m4a", "aac"],
    )
    if uploaded:
        suffix = Path(uploaded.name).suffix
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(uploaded.read())
        tmp.flush()
        audio_path = tmp.name
        st.audio(uploaded)

st.write("")
run_btn = st.button("▶  Run pipeline", use_container_width=True)

if run_btn:
    with st.spinner("Running pipeline… this may take a moment."):
        result = run_pipeline(
            input_type=input_type.lower().split()[0],
            text_input=text_input,
            audio_path=audio_path,
            target_language=target_language,
        )

    if result["error"]:
        st.error(f"❌ {result['error']}")
    else:
        st.divider()
        st.subheader("Results")

        if result["transcript"] is not None:
            st.markdown('<div class="step-label">① Transcript</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-box">{result["transcript"]}</div>', unsafe_allow_html=True)

        if input_type == "Text" and text_input:
            st.markdown('<div class="step-label">① Original text</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-box">{text_input.strip()}</div>', unsafe_allow_html=True)

        st.markdown('<div class="step-label">② Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{result["summary"]}</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="step-label">③ Translation ({target_language})</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{result["translation"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="step-label">④ Generated speech</div>', unsafe_allow_html=True)
        st.audio(result["audio_bytes"], format="audio/wav")

        st.success("✅ Pipeline complete!")