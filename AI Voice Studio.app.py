import streamlit as st
from gtts import gTTS
from langdetect import detect
from deep_translator import GoogleTranslator
import speech_recognition as sr
from pydub import AudioSegment
from pypdf import PdfReader
from docx import Document
import tempfile
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Voice Studio", layout="wide")

# ---------- CUSTOM UI ----------
st.markdown("""
<style>
.main {background-color: #0f172a;}
h1, h2, h3, h4 {color: #e2e8f0;}
.stButton>button {
    background-color: #14b8a6;
    color: white;
    border-radius: 8px;
}
.stTextArea textarea {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "usage" not in st.session_state:
    st.session_state.usage = 0
if "files" not in st.session_state:
    st.session_state.files = 0

# ---------- HEADER ----------
st.title("🎙️ AI Voice Studio")
st.caption("All-in-One Voice, Text, Video & PDF AI Platform")

# ---------- HELPERS ----------
def detect_lang(text):
    try:
        return detect(text)
    except:
        return "en"

def tts(text, lang):
    fp = io.BytesIO()
    gTTS(text=text, lang=lang).write_to_fp(fp)
    fp.seek(0)
    return fp

def translate(text, target):
    return GoogleTranslator(source='auto', target=target).translate(text)

def speech_to_text(path):
    r = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio = r.record(source)
    return r.recognize_google(audio)

def read_pdf(file):
    reader = PdfReader(file)
    return "".join([p.extract_text() or "" for p in reader.pages])

def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def create_pdf(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    doc.build([Paragraph(text, styles["Normal"])])
    buffer.seek(0)
    return buffer

# ---------- TABS ----------
tabs = st.tabs([
    "🔊 Text→Voice",
    "🎤 Voice→Text",
    "🌍 Translator",
    "📄 File Reader",
    "🎬 Video Reader",
    "🧾 Text→PDF",
    "📊 Dashboard"
])

# ---------- TEXT TO VOICE ----------
with tabs[0]:
    st.subheader("Text to Voice")

    text = st.text_area("Enter text")

    if st.button("Generate Voice"):
        lang = detect_lang(text)
        audio = tts(text, lang)

        st.audio(audio)
        st.download_button("Download Audio", audio, "voice.mp3")

        st.session_state.history.append(f"TTS: {text[:50]}")
        st.session_state.usage += len(text)

# ---------- VOICE TO TEXT ----------
with tabs[1]:
    st.subheader("Voice to Text")

    file = st.file_uploader("Upload audio", type=["wav","mp3","ogg"])

    if file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            path = tmp.name

        sound = AudioSegment.from_file(path)
        wav_path = path + ".wav"
        sound.export(wav_path, format="wav")

        if st.button("Convert"):
            text = speech_to_text(wav_path)
            st.text_area("Result", text)

            st.session_state.history.append("Voice → Text")
            st.session_state.files += 1

# ---------- TRANSLATOR ----------
with tabs[2]:
    st.subheader("Translator")

    text = st.text_area("Enter text")
    lang = st.selectbox("Target", ["en","ur","hi","ar","fr"])

    if st.button("Translate"):
        result = translate(text, lang)
        st.text_area("Result", result)

        st.session_state.history.append("Translation used")

# ---------- FILE READER ----------
with tabs[3]:
    st.subheader("File Reader")

    file = st.file_uploader("Upload file", type=["pdf","docx","txt"])

    if file:
        ext = file.name.split(".")[-1]

        if ext == "pdf":
            content = read_pdf(file)
        elif ext == "docx":
            content = read_docx(file)
        else:
            content = file.read().decode()

        st.text_area("Content", content[:2000])

        st.session_state.files += 1

# ---------- VIDEO READER ----------
with tabs[4]:
    st.subheader("Video to Text")

    video = st.file_uploader("Upload video", type=["mp4","mov","avi"])

    if video:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(video.read())
            path = tmp.name

        audio = AudioSegment.from_file(path)
        audio_path = path + ".wav"
        audio.export(audio_path, format="wav")

        if st.button("Extract Text"):
            text = speech_to_text(audio_path)
            st.text_area("Transcript", text)

            st.session_state.history.append("Video → Text")
            st.session_state.files += 1

# ---------- TEXT TO PDF ----------
with tabs[5]:
    st.subheader("Text to PDF")

    text = st.text_area("Enter text")

    if st.button("Generate PDF"):
        pdf = create_pdf(text)

        st.download_button(
            "Download PDF",
            pdf,
            "output.pdf",
            mime="application/pdf"
        )

        st.session_state.history.append("PDF Generated")

# ---------- DASHBOARD ----------
with tabs[6]:
    st.subheader("📊 Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Characters Used", st.session_state.usage)
    col2.metric("Files Processed", st.session_state.files)
    col3.metric("Total Actions", len(st.session_state.history))

    st.divider()

    st.write("### 📈 Activity Timeline")

    for i, item in enumerate(reversed(st.session_state.history[-10:])):
        st.write(f"{i+1}. {item}")

    st.divider()

    st.write("### 🚀 Features Available")
    st.markdown("""
    - 🔊 Text to Voice  
    - 🎤 Voice to Text  
    - 🌍 Translation  
    - 📄 File Reader  
    - 🎬 Video Reader  
    - 🧾 PDF Generator  
    """)
