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
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Voice Studio", layout="wide")

# ---------- UI ----------
st.markdown("""
<style>
body {background-color:#0f172a;color:white;}
.stButton>button {
    background-color:#14b8a6;
    color:white;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "usage" not in st.session_state:
    st.session_state.usage = 0

# ---------- SIDEBAR ----------
st.sidebar.title("🎙️ AI Voice Studio")
page = st.sidebar.radio("Menu", [
    "🎤 Playground",
    "🎧 Voice to Text",
    "🌍 Translator",
    "📄 File Reader",
    "🎬 Video Reader",
    "🧾 Text to PDF",
    "📊 Dashboard"
])

# ---------- HELPERS ----------
def detect_lang(text):
    try:
        return detect(text)
    except:
        return "en"

def safe_tts(text, lang):
    try:
        fp = io.BytesIO()
        gTTS(text=text, lang=lang).write_to_fp(fp)
        fp.seek(0)
        return fp
    except Exception as e:
        return None

def safe_translate(text, target):
    try:
        return GoogleTranslator(source='auto', target=target).translate(text)
    except:
        return "Translation failed"

def safe_stt(audio_path):
    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
        return r.recognize_google(audio)
    except Exception as e:
        return f"Error: {str(e)}"

def safe_audio_convert(path):
    try:
        sound = AudioSegment.from_file(path)
        wav_path = path + ".wav"
        sound.export(wav_path, format="wav")
        return wav_path
    except:
        return None

def read_pdf(file):
    try:
        reader = PdfReader(file)
        return "".join([p.extract_text() or "" for p in reader.pages])
    except:
        return ""

def read_docx(file):
    try:
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    except:
        return ""

def create_pdf(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    doc.build([Paragraph(text, styles["Normal"])])
    buffer.seek(0)
    return buffer

# ---------- PLAYGROUND ----------
if page == "🎤 Playground":
    st.title("🎤 Voice Playground")

    text = st.text_area("Enter text")

    col1, col2 = st.columns([3,1])

    with col1:
        if st.button("Generate Voice"):
            if not text.strip():
                st.warning("Enter text first")
            else:
                lang = detect_lang(text)
                audio = safe_tts(text, lang)

                if audio:
                    st.audio(audio)
                    st.download_button("Download", audio, "voice.mp3")

                    st.session_state.history.append(text[:50])
                    st.session_state.usage += len(text)
                else:
                    st.error("Voice generation failed")

    with col2:
        lang = st.selectbox("Translate", ["none","en","ur","hi","ar"])
        if st.button("Translate"):
            if text.strip():
                if lang != "none":
                    result = safe_translate(text, lang)
                    st.text_area("Result", result)
            else:
                st.warning("Enter text")

# ---------- VOICE TO TEXT ----------
elif page == "🎧 Voice to Text":
    st.title("🎧 Voice to Text")

    file = st.file_uploader("Upload audio", type=["wav","mp3","ogg"])

    if file:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(file.read())
                path = tmp.name

            wav = safe_audio_convert(path)

            if not wav:
                st.error("Audio conversion failed (ffmpeg issue)")
            else:
                if st.button("Convert"):
                    result = safe_stt(wav)
                    st.text_area("Result", result)
                    st.session_state.history.append("Voice→Text")

        except:
            st.error("Unsupported file")

# ---------- TRANSLATOR ----------
elif page == "🌍 Translator":
    st.title("🌍 Translator")

    text = st.text_area("Enter text")
    lang = st.selectbox("Language", ["en","ur","hi","ar","fr"])

    if st.button("Translate"):
        if text.strip():
            result = safe_translate(text, lang)
            st.text_area("Result", result)
        else:
            st.warning("Enter text")

# ---------- FILE READER ----------
elif page == "📄 File Reader":
    st.title("📄 File Reader")

    file = st.file_uploader("Upload file", type=["pdf","docx","txt"])

    if file:
        ext = file.name.split(".")[-1]

        if ext == "pdf":
            content = read_pdf(file)
        elif ext == "docx":
            content = read_docx(file)
        else:
            content = file.read().decode(errors="ignore")

        if content:
            st.text_area("Content", content[:2000])
        else:
            st.warning("No readable content")

# ---------- VIDEO READER ----------
elif page == "🎬 Video Reader":
    st.title("🎬 Video to Text")

    video = st.file_uploader("Upload video", type=["mp4","mov","avi"])

    if video:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(video.read())
                path = tmp.name

            wav = safe_audio_convert(path)

            if not wav:
                st.error("Video conversion failed")
            else:
                if st.button("Extract Text"):
                    result = safe_stt(wav)
                    st.text_area("Transcript", result)
                    st.session_state.history.append("Video→Text")

        except:
            st.error("Unsupported video")

# ---------- TEXT TO PDF ----------
elif page == "🧾 Text to PDF":
    st.title("🧾 Text to PDF")

    text = st.text_area("Enter text")

    if st.button("Generate PDF"):
        if text.strip():
            pdf = create_pdf(text)
            st.download_button("Download PDF", pdf, "output.pdf")
            st.session_state.history.append("PDF created")
        else:
            st.warning("Enter text")

# ---------- DASHBOARD ----------
elif page == "📊 Dashboard":
    st.title("📊 Dashboard")

    col1, col2 = st.columns(2)
    col1.metric("Characters Used", st.session_state.usage)
    col2.metric("Total Actions", len(st.session_state.history))

    st.write("### Activity")
    for h in st.session_state.history[-10:]:
        st.write("-", h)
