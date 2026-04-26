import streamlit as st
from gtts import gTTS
import speech_recognition as sr
from langdetect import detect
from pypdf import PdfReader
from docx import Document
from pydub import AudioSegment
import tempfile
import io
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Voice Studio", page_icon="🎙️", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
body {background-color: #0f172a; color: white;}
</style>
""", unsafe_allow_html=True)

st.title("🎙️ AI Voice Studio")
st.caption("Text ↔ Speech | Multi-language | File Reader")

# ---------- HELPERS ----------

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

def text_to_speech(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except Exception as e:
        return None

def speech_to_text(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except Exception as e:
        return f"Error: {str(e)}"

def read_pdf(file):
    text = ""
    try:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    except:
        pass
    return text

def read_docx(file):
    text = ""
    try:
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except:
        pass
    return text

def read_txt(file):
    try:
        return file.read().decode("utf-8")
    except:
        return ""

# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(["🔊 Text → Speech", "🎤 Speech → Text", "📄 File Reader"])

# ---------- TAB 1 ----------
with tab1:
    st.subheader("Text to Speech")

    text_input = st.text_area("Enter text")

    lang_option = st.selectbox(
        "Language",
        ["auto", "en", "ur", "hi", "ar", "fr", "de", "es"]
    )

    if st.button("Generate Voice"):
        if not text_input.strip():
            st.warning("Enter text first")
        else:
            lang = detect_language(text_input) if lang_option == "auto" else lang_option
            audio = text_to_speech(text_input, lang)

            if audio:
                st.success(f"Detected Language: {lang}")
                st.audio(audio, format="audio/mp3")

                st.download_button(
                    "Download",
                    audio,
                    file_name="voice.mp3"
                )
            else:
                st.error("Failed to generate voice")

# ---------- TAB 2 ----------
with tab2:
    st.subheader("Speech to Text")

    audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "ogg"])

    if audio_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(audio_file.read())
            temp_path = tmp.name

        try:
            # Convert to WAV
            sound = AudioSegment.from_file(temp_path)
            wav_path = temp_path + ".wav"
            sound.export(wav_path, format="wav")

            if st.button("Transcribe"):
                result = speech_to_text(wav_path)
                st.text_area("Result", result)

        except Exception as e:
            st.error("Audio format not supported")

# ---------- TAB 3 ----------
with tab3:
    st.subheader("File to Speech")

    file = st.file_uploader("Upload PDF / DOCX / TXT", type=["pdf", "docx", "txt"])

    if file:
        ext = file.name.split(".")[-1]

        if ext == "pdf":
            content = read_pdf(file)
        elif ext == "docx":
            content = read_docx(file)
        else:
            content = read_txt(file)

        if content:
            st.text_area("Preview", content[:2000])

            if st.button("Convert to Voice"):
                lang = detect_language(content)
                audio = text_to_speech(content[:2000], lang)

                if audio:
                    st.audio(audio)
                    st.download_button("Download", audio, "file.mp3")
                else:
                    st.error("Conversion failed")
        else:
            st.warning("No text found")
