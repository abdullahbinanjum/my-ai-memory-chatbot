from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables (ensure your .env file exists if you use it for anything)
load_dotenv()

# --- Streamlit Configuration ---
st.set_page_config(
    page_title="DeepThink AI Assistant", # New Page Title
    layout="centered",
    initial_sidebar_state="auto" # Default
)

# --- Theme Toggle (Dark/Light Mode) ---
if "theme" not in st.session_state:
    st.session_state.theme = "light" # Default to light theme

# Toggle button for theme - New text and emoji
if st.button("🌟 Switch Theme: " + ("🌙 Dark" if st.session_state.theme == "light" else "☀️ Light")):
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()

# Apply custom CSS based on the current theme - UNIQUE COLORS
if st.session_state.theme == "dark":
    # Dark Mode - Deep Blue/Purple Palette
    background_color = "#1a1a2e" # Dark Blue-Violet
    text_color = "#e0e0e0"       # Off-white
    header_color = "#b2e0f0"     # Light Cyan for headers
    chat_bg_user = "#332a5a"     # Darker Blue-Purple for user bubbles
    chat_bg_bot = "#2a2144"      # Even darker Blue-Purple for bot bubbles
    border_color = "#4c4c7a"     # Muted Purple for borders
    button_bg = "#4CAF50" # Main action button green
    button_hover = "#45a049"
    input_focus_border = "#90EE90" # Light Green
else:
    # Light Mode - Soft Green/Grey Palette
    background_color = "#f0f8ff" # AliceBlue
    text_color = "#333333"       # Dark text
    header_color = "#32CD32"     # Lime Green for headers
    chat_bg_user = "#e6ffe6"     # Very light green for user bubbles
    chat_bg_bot = "#f5f5f5"      # Light grey for bot bubbles
    border_color = "#a3d9a3"     # Muted Green for borders
    button_bg = "#4CAF50" # Main action button green
    button_hover = "#45a049"
    input_focus_border = "#00BFFF" # Deep Sky Blue

st.markdown(f"""
    <style>
    /* General Page Styling */
    .stApp {{
        background-color: {background_color};
        color: {text_color};
        font-family: 'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}

    /* Title Styling - Changed font, added shadow */
    h1 {{
        color: {header_color};
        text-align: center;
        font-family: 'Roboto', sans-serif;
        font-weight: 900; /* Bolder */
        letter-spacing: 2px; /* More spacing */
        text-shadow: 2px 2px 5px rgba(0,0,0,0.2); /* Subtle shadow */
        margin-bottom: 25px; /* More space below title */
    }}

    /* Input field styling */
    .stTextInput > div > div > input {{
        background-color: {background_color};
        color: {text_color};
        border: 1px solid {border_color};
        border-radius: 25px; /* More rounded */
        padding: 12px 20px; /* Increased padding */
        font-size: 17px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15); /* Stronger shadow */
        transition: all 0.3s ease; /* Smooth transition on focus */
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {input_focus_border}; /* Highlight on focus */
        box-shadow: 0 0 0 3px rgba(144, 238, 144, 0.5); /* Glowing effect */
        outline: none; /* Remove default outline */
    }}
    .stTextInput > label {{
        color: {text_color};
        font-size: 16px;
        margin-bottom: 5px;
    }}

    /* Button Styling - More rounded, distinct colors */
    .stButton > button {{
        background-color: {button_bg};
        color: white;
        border: none;
        padding: 12px 25px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 17px;
        margin: 5px 2px;
        cursor: pointer;
        border-radius: 25px; /* More rounded */
        transition: background-color 0.3s ease, transform 0.2s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    .stButton > button:hover {{
        background-color: {button_hover};
        transform: translateY(-2px); /* Slight lift on hover */
    }}
    .stButton > button:active {{
        background-color: #3e8e41;
        transform: translateY(0); /* Return on click */
    }}

    /* Slider Styling */
    .stSlider > label {{
        color: {text_color};
    }}
    .stSlider .st-fx {{ /* track */
        background-color: {border_color};
    }}
    .stSlider .st-fy {{ /* thumb */
        background-color: {button_bg};
        border: 2px solid {button_hover};
    }}

    /* Chat bubble styling - More pronounced rounding, different shadows */
    .chat-bubble {{
        padding: 15px 20px; /* Increased padding */
        border-radius: 15px; /* Less aggressive rounding for overall bubble */
        margin-bottom: 12px; /* More space between bubbles */
        max-width: 85%; /* Slightly wider bubbles */
        word-wrap: break-word;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1); /* Deeper shadow */
        line-height: 1.6; /* Increased line height for readability */
    }}
    .user-bubble {{
        background-color: {chat_bg_user};
        color: {text_color};
        align-self: flex-end;
        border-top-left-radius: 15px; /* Round all but one corner for a distinct look */
        border-top-right-radius: 15px;
        border-bottom-left-radius: 15px;
        border-bottom-right-radius: 5px;
        margin-left: auto; /* Push user bubble to the right */
    }}
    .bot-bubble {{
        background-color: {chat_bg_bot};
        color: {text_color};
        align-self: flex-start;
        border-top-left-radius: 15px;
        border-top-right-radius: 15px;
        border-bottom-right-radius: 15px;
        border-bottom-left-radius: 5px;
        margin-right: auto; /* Push bot bubble to the left */
    }}
    .chat-container {{
        display: flex;
        flex-direction: column;
        padding: 20px; /* More padding around chat area */
        background-color: rgba(0,0,0,0.05); /* Slightly darker background for chat area */
        border-radius: 15px;
        margin-bottom: 30px; /* More space below chat area */
        border: 1px solid {border_color};
        box-shadow: inset 0 0 10px rgba(0,0,0,0.05); /* Inner shadow */
    }}
    </style>
""", unsafe_allow_html=True)


# --- Main Application Title & Subtitle ---
st.title("🧠 DeepThink AI Assistant") # Changed title and emoji
st.markdown("##### *Your intelligent companion for all queries.*") # Added a subtitle

# --- Initialize chat history ---
if "chat_history" not in st.session_state:
    # Changed system message to be more engaging
    st.session_state.chat_history = [("system", "Hello! I am DeepThink AI. How can I assist you today? Feel free to ask anything!")]

# --- Temperature control ---
temperature = st.slider(
    "💡 Adjust Creativity Level (Temperature)", # Changed slider text
    0.0, 1.0, 0.7,
    help="Lower values make me more focused and deterministic (predictable), higher values make me more creative and adventurous (random)."
)

# --- Model and parser setup ---
llm = Ollama(model="deepseek-r1:7b", temperature=temperature) # Model remains the same
output_parser = StrOutputParser()

# --- Clear Chat Button - New text and emoji ---
if st.button("🔄 Start New Conversation", help="Clears the entire conversation history and starts fresh."):
    st.session_state.chat_history = [("system", "Hello! I am DeepThink AI. How can I assist you today? Feel free to ask anything!")]
    st.rerun()

st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
# --- Chat history display with improved UI and custom prefixes ---
for role, message in st.session_state.chat_history:
    if role == "user":
        # Changed "You:" to "👤 User:"
        st.markdown(f"<div class='chat-bubble user-bubble'><b>👤 User:</b> {message}</div>", unsafe_allow_html=True)
    elif role == "assistant":
        # Changed "Bot:" to "🤖 DeepThink:"
        st.markdown(f"<div class='chat-bubble bot-bubble'><b>🤖 DeepThink:</b> {message}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# --- Input field and send button ---
with st.container():
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            user_input = st.text_input(
                "💬 Share your thoughts...", # New placeholder text
                key="user_input",
                label_visibility="collapsed"
            )
        with col2:
            submitted = st.form_submit_button("🚀 Send") # New emoji for send button

# --- If message submitted ---
if submitted and user_input:
    st.session_state.chat_history.append(("user", user_input))
    prompt = ChatPromptTemplate.from_messages(st.session_state.chat_history)
    chain = prompt | llm | output_parser

    with st.spinner("✨ Pondering the vastness of knowledge..."): # New spinner text
        try:
            response = chain.invoke({})
            st.session_state.chat_history.append(("assistant", response))
            st.rerun()
        except Exception as e:
            st.session_state.chat_history.append(("assistant", f"Error: My core processing unit encountered an issue. Please ensure Ollama server is running and the model '{llm.model}' is available. Details: {e}"))
            st.rerun()