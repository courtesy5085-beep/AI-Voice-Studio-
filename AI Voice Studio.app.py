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
st.set_page_config(page_title="AI Voice Studio", layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
body {background-color: #0f172a;}
h1, h2, h3 {color: white;}
.stButton>button {
    background-color: #14b8a6;
    color: white;
    border-radius: 8px;
}
.sidebar .sidebar-content {
    background-color: #020617;
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

page = st.sidebar.radio(
    "Navigation",
    [
        "🎤 Playground",
        "🎧 Voice to Text",
        "🌍 Translator",
        "📄 File Reader",
        "🎬 Video Reader",
        "🧾 Text to PDF",
        "📊 Dashboard"
    ]
)

st.sidebar.markdown("---")
st.sidebar.write("⚡ Powered by AI")
st.sidebar.write("Free Version")

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

# ---------- PLAYGROUND ----------
if page == "🎤 Playground":
    st.title("🎤 Voice Playground")

    text = st.text_area("Enter text")

    col1, col2 = st.columns([3,1])

    with col1:
        if st.button("🔊 Generate Voice"):
            lang = detect_lang(text)
            audio = tts(text, lang)

            st.audio(audio)
            st.download_button("Download", audio, "voice.mp3")

            st.session_state.history.append(text[:50])
            st.session_state.usage += len(text)

    with col2:
        lang_select = st.selectbox("Language", ["auto","en","ur","hi","ar"])

        if st.button("🌍 Translate"):
            if lang_select != "auto":
                text = translate(text, lang_select)
                st.text_area("Translated", text)

# ---------- VOICE TO TEXT ----------
elif page == "🎧 Voice to Text":
    st.title("🎧 Voice to Text")

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

# ---------- TRANSLATOR ----------
elif page == "🌍 Translator":
    st.title("🌍 Translator")

    text = st.text_area("Enter text")
    lang = st.selectbox("Target Language", ["en","ur","hi","ar","fr"])

    if st.button("Translate"):
        result = translate(text, lang)
        st.text_area("Result", result)

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
            content = file.read().decode()

        st.text_area("Content", content[:2000])

# ---------- VIDEO READER ----------
elif page == "🎬 Video Reader":
    st.title("🎬 Video to Text")

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
elif page == "🧾 Text to PDF":
    st.title("🧾 Text to PDF")

    text = st.text_area("Enter text")

    if st.button("Generate PDF"):
        pdf = create_pdf(text)

        st.download_button(
            "Download PDF",
            pdf,
            "output.pdf",
            mime="application/pdf"
        )

# ---------- DASHBOARD ----------
elif page == "📊 Dashboard":
    st.title("📊 Dashboard")

    col1, col2 = st.columns(2)

    col1.metric("Characters Used", st.session_state.usage)
    col2.metric("Total Actions", len(st.session_state.history))

    st.write("### Recent Activity")
    for h in st.session_state.history[-5:]:
        st.write("-", h)
