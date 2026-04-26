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

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Studio Pro", layout="wide")

# ---------- SESSION ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "usage" not in st.session_state:
    st.session_state.usage = 0

# ---------- HEADER ----------
st.title("🎙️ AI Studio PRO")
st.caption("Voice | Text | Video | PDF Tools in One App")

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
    text = ""
    reader = PdfReader(file)
    for p in reader.pages:
        text += p.extract_text() or ""
    return text

def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def create_pdf(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = [Paragraph(text, styles["Normal"])]
    doc.build(content)
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
    text = st.text_area("Enter text")

    if st.button("Generate Voice"):
        lang = detect_lang(text)
        audio = tts(text, lang)

        st.audio(audio)
        st.download_button("Download", audio, "voice.mp3")

        st.session_state.history.append(text)
        st.session_state.usage += len(text)

# ---------- VOICE TO TEXT ----------
with tabs[1]:
    audio_file = st.file_uploader("Upload audio", type=["wav","mp3","ogg"])

    if audio_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(audio_file.read())
            path = tmp.name

        sound = AudioSegment.from_file(path)
        wav_path = path + ".wav"
        sound.export(wav_path, format="wav")

        if st.button("Convert"):
            text = speech_to_text(wav_path)
            st.text_area("Result", text)

# ---------- TRANSLATOR ----------
with tabs[2]:
    text = st.text_area("Enter text to translate")

    lang = st.selectbox("Target Language", ["en","ur","hi","ar","fr"])

    if st.button("Translate"):
        result = translate(text, lang)
        st.text_area("Translated", result)

# ---------- FILE READER ----------
with tabs[3]:
    file = st.file_uploader("Upload PDF/DOCX/TXT", type=["pdf","docx","txt"])

    if file:
        ext = file.name.split(".")[-1]

        if ext == "pdf":
            content = read_pdf(file)
        elif ext == "docx":
            content = read_docx(file)
        else:
            content = file.read().decode()

        st.text_area("Content", content[:2000])

# ---------- VIDEO READER ----------
with tabs[4]:
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

# ---------- TEXT TO PDF ----------
with tabs[5]:
    text = st.text_area("Enter text for PDF")

    if st.button("Generate PDF"):
        pdf = create_pdf(text)

        st.download_button(
            "Download PDF",
            pdf,
            "output.pdf",
            mime="application/pdf"
        )

# ---------- DASHBOARD ----------
with tabs[6]:
    st.metric("Characters Used", st.session_state.usage)

    st.write("### History")
    for h in st.session_state.history[-5:]:
        st.write("-", h[:50])
