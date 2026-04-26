import streamlit as st
from gtts import gTTS
from langdetect import detect
from deep_translator import GoogleTranslator
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import io
import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Voice Studio Pro", layout="wide")

# ---------- SESSION ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "usage" not in st.session_state:
    st.session_state.usage = 0

# ---------- HEADER ----------
st.title("🎙️ AI Voice Studio PRO")
st.caption("Advanced Voice AI Toolkit")

# ---------- HELPERS ----------

def detect_lang(text):
    try:
        return detect(text)
    except:
        return "en"

def translate_text(text, target):
    try:
        return GoogleTranslator(source='auto', target=target).translate(text)
    except:
        return text

def generate_tts(text, lang):
    tts = gTTS(text=text, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

def generate_srt(text):
    lines = text.split(".")
    srt = ""
    for i, line in enumerate(lines):
        start = i * 2
        end = start + 2
        srt += f"{i+1}\n00:00:{start:02d} --> 00:00:{end:02d}\n{line.strip()}\n\n"
    return srt

# ---------- SIDEBAR ----------
st.sidebar.title("⚙️ Controls")

voice_style = st.sidebar.selectbox(
    "Voice Style",
    ["Normal", "Male", "Female", "Deep", "Fast"]
)

target_lang = st.sidebar.selectbox(
    "Translate To",
    ["None", "en", "ur", "hi", "ar"]
)

speed = st.sidebar.slider("Playback Speed", 0.5, 2.0, 1.0)

# ---------- MAIN ----------
tabs = st.tabs(["🎤 Voice Generator", "📜 Subtitle Tool", "📊 Dashboard"])

# ---------- TAB 1 ----------
with tabs[0]:
    st.subheader("Text → Voice + AI Tools")

    text = st.text_area("Enter your script")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✨ Improve Text"):
            text = text.capitalize() + "..."
            st.success("Improved!")

    with col2:
        if st.button("🌍 Translate"):
            if target_lang != "None":
                text = translate_text(text, target_lang)
                st.success("Translated!")

    with col3:
        if st.button("🔊 Generate Voice"):
            lang = detect_lang(text)

            audio = generate_tts(text, lang)

            st.audio(audio)

            st.download_button("Download", audio, "voice.mp3")

            # Save history
            st.session_state.history.append(text)
            st.session_state.usage += len(text)

# ---------- TAB 2 ----------
with tabs[1]:
    st.subheader("Subtitle Generator (SRT)")

    sub_text = st.text_area("Enter script for subtitles")

    if st.button("Generate SRT"):
        srt = generate_srt(sub_text)
        st.code(srt)

        st.download_button("Download SRT", srt, "subtitles.srt")

# ---------- TAB 3 ----------
with tabs[2]:
    st.subheader("User Dashboard")

    st.metric("Total Characters Used", st.session_state.usage)

    st.write("### History")
    for item in st.session_state.history[-5:]:
        st.write("-", item[:50])
