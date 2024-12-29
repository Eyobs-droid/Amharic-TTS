import asyncio
import edge_tts
import streamlit as st
import base64
import os
import tempfile
from pydub import AudioSegment
import time
import random

# Set page config
st.set_page_config(
    page_title="Amharic Text-to-Speech",
    page_icon="🗣️",
    layout="wide"
)

# Background style
st.markdown(f"""
    <style>
    /* Main content styling */
    .main {{
        padding: 2rem;
    }}

    /* Background image styling */
    .stApp {{
        background-image: url("data:image/png;base64");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Add overlay to make text more readable */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.85);  /* White overlay with 85% opacity */
        pointer-events: none;
        z-index: 0;
    }}

    /* Make sure content appears above overlay */
    .main .block-container {{
        position: relative;
        z-index: 1;
    }}

    /* Title styling with gradient and animation */
    .gradient-text {{
        position: relative;
        background: linear-gradient(45deg, #1e3c72, #2a5298);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        animation: glow 3s ease-in-out infinite;
        margin-bottom: 2rem;
        z-index: 1;
    }}

    .title-amharic {{
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }}

    .title-english {{
        font-size: 1.5rem;
        opacity: 0.9;
    }}

    /* Glowing animation */
    @keyframes glow {{
        0% {{
            box-shadow: 0 0 5px rgba(30, 60, 114, 0.3);
        }}
        50% {{
            box-shadow: 0 0 20px rgba(42, 82, 152, 0.5);
        }}
        100% {{
            box-shadow: 0 0 5px rgba(30, 60, 114, 0.3);
        }}
    }}

    /* Sidebar styling */
    .sidebar-content {{
        padding: 1rem;
        position: relative;
        z-index: 1;
    }}
    .sidebar .sidebar-content {{
        background-color: rgba(248, 249, 250, 0.95);
    }}
    .sidebar-section {{
        margin-bottom: 2rem;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .icon-header {{
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1f77b4;
    }}

    /* Input area styling */
    .stTextInput, .stTextArea {{
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}

    /* Radio buttons styling */
    .stRadio > label {{
        background-color: rgba(248, 249, 250, 0.9);
        padding: 10px 15px;
        border-radius: 5px;
        margin: 5px;
        transition: all 0.3s ease;
    }}
    .stRadio > label:hover {{
        background-color: #e9ecef;
    }}

    audio {{
        display: none;
    }}
    </style>
    """, unsafe_allow_html=True)

# Custom title with gradient and animation
st.markdown("""
    <div class="gradient-text">
        <div class="title-amharic">🎙️ የ አማርኛ  ንግግር  ስርዓት</div>
        <div class="title-english">Amharic Text-to-Speech System</div>
    </div>
    """, unsafe_allow_html=True)

# Sample Amharic texts
SAMPLE_TEXTS = {
    "Greetings": [
        "ሰላም እንደምን ነዎት?",
        "እንደምን አደርክ/ሽ?",
        "ጤና ይስጥልኝ",
    ],
    "Common Phrases": [
        "እባክዎ ይታገሱ",
        "አመሰግናለሁ",
        "ይቅርታ",
        "እንኳን ደህና መጣህ/ሽ",
    ],
    "Sentences": [
        "ኢትዮጵያ የተለያዩ ባህሎች መስተጋብር ያላት ሀገር ናት።",
        "አዲስ አበባ የኢትዮጵያ ዋና ከተማ ናት።",
        "የኢትዮጵያ ሰዎች በጣም ቆንጆ ናቸው።",
    ]
}

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    # Voice selection with mapping
    VOICE_OPTIONS = {
        "Mekdes (Female)": "am-ET-MekdesNeural",
        "Ameha (Male)": "am-ET-AmehaNeural"
    }

    voice_display = st.selectbox(
        "Select Voice:",
        list(VOICE_OPTIONS.keys()),
        index=0,
        help="Choose between female (Mekdes) or male (Ameha) voice"
    )
    voice_option = VOICE_OPTIONS[voice_display]

    # Speed control
    speed = st.slider(
        "Speech Speed:",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="Adjust the speed of speech"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Sample texts section
    st.markdown("### 📖 Sample Texts")
    category = st.selectbox("Select Category:", list(SAMPLE_TEXTS.keys()))

    if st.button("Try Random Sample"):
        selected_text = random.choice(SAMPLE_TEXTS[category])
        st.session_state.sample_text = selected_text

    st.markdown("<br>", unsafe_allow_html=True)

    # About section
    st.markdown("### ℹ️ About This System")
    st.markdown("""
        This is an Amharic Text-to-Speech system that converts written Amharic text into natural-sounding speech.

        Features:
        - Natural voice synthesis
        - Adjustable speech speed
        - Male and female voices
        - Sample text categories
    """)

async def text_to_speech(text: str, voice: str, speed: float) -> str:
    """Generate speech from text using edge-tts."""
    try:
        communicate = edge_tts.Communicate(text, voice, rate=f"{int((speed-1)*100):+d}%")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        await communicate.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")


def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true" onended="this.currentTime=0;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Store the last generated audio in session state
if 'last_audio' not in st.session_state:
    st.session_state.last_audio = None

# Text input area
if 'sample_text' in st.session_state and st.session_state.sample_text:
    text_input = st.text_area(
        "Type your Amharic text here:",
        value=st.session_state.sample_text,
        placeholder="እባክዎ እዚህ ይጻፉ...",
        height=150
    )
    st.session_state.sample_text = ""
else:
    text_input = st.text_area(
        "Type your Amharic text here:",
        placeholder="እባክዎ እዚህ ይጻፉ...",
        height=150
    )

# Audio container
audio_placeholder = st.empty()

# Generate and play audio when text changes
if text_input:
    audio_file = asyncio.run(text_to_speech(text_input, voice_option, speed))
    if audio_file:
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        st.session_state.last_audio = base64.b64encode(audio_data).decode()
        with audio_placeholder:
            st.markdown(f"""
                <audio autoplay="true" onended="this.currentTime=0;">
                    <source src="data:audio/mp3;base64,{st.session_state.last_audio}" type="audio/mp3">
                </audio>
                """, unsafe_allow_html=True)
        os.unlink(audio_file)
        time.sleep(0.1)
elif st.session_state.last_audio:
    with audio_placeholder:
        st.markdown(f"""
            <audio autoplay="true" onended="this.currentTime=0;">
                <source src="data:audio/mp3;base64,{st.session_state.last_audio}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)
