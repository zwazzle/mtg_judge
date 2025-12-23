import streamlit as st
import os
import requests
from openai import OpenAI
from streamlit_searchbox import st_searchbox

# Eigene Module importieren
from database import MTG_VOCABULARY, SPECIAL_CASES, SYSTEM_GUIDELINES
from mtg_logic import get_scryfall_rulings, get_rules_context, search_scryfall

# 1. PAGE CONFIG
st.set_page_config(
    page_title="Monster Magic Mastermind",
    page_icon="🧙‍♂️", 
    layout="wide"
)

# 2. CSS FÜR HOVER-EFFEKT (Tooltips)
st.markdown("""
    <style>
    /* Styling für den verlinkten Kartennamen */
    .card-hover {
        color: #ff4b4b !important;
        text-decoration: underline;
        cursor: help;
        position: relative;
        font-weight: bold;
    }
    /* Das Bild, das beim Hover erscheint */
    .card-hover:hover::after {
        content: "";
        background-image: var(--bg-img);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        width: 200px;
        height: 280px;
        background-size: contain;
        background-repeat: no-repeat;
        z-index: 1000;
        border-radius: 10px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
        background-color: #1e1e1e;
    }
    </style>
""", unsafe_allow_html=True)

# 3. CONFIG & SECRETS
if "DEEPSEEK_API_KEY" in st.secrets:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
else:
    api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 4. SESSION STATE
if "rules_lines" not in st.session_state:
    try:
        with open("rules.txt", "r", encoding="utf-8") as f:
            st.session_state.rules_lines = f.readlines()
    except FileNotFoundError:
        st.session_state.rules_lines = []

if 'my_cards' not in st.session_state: st.session_state.my_cards = []
if 'messages' not in st.session_state: st.session_state.messages = []

# --- UI ---
st.title("🧙‍♂️ Monster Magic Mastermind")

# KARTEN-MANAGEMENT
with st.expander("🎴 Karten-Auswahl verwalten", expanded=True):
    search_key = "card_search"
    selected = st_searchbox(search_scryfall, key=search_key)
    
    if selected:
        if selected not in [c['name'] for c in st.session_state.my_cards]:
            res = requests.get(f"https://api.scryfall.com/cards/named?exact={selected}")
            if res.status_code == 200:
                st.session_state.my_cards.append(res.json())
                if search_key in st.session_state: del st.session_state[search_key]
                st.rerun()

    cols = st.columns(6)
    for i, card in enumerate(st.session_state.my_cards):
        with cols[i % 6]:
            if 'image_uris' in card:
                st.image(card['image_uris']['normal'], width=150)
            if st.button("Löschen", key=f"del_{i}"):
                st.session_state.my_cards.pop(i)
                st.rerun()

# CHAT VERLAUF (mit HTML-Support für Hover)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"], unsafe_allow_html=True)

# CHAT EINGABE
if prompt := st.chat_input("Deine Regelfrage..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Bild-Daten für die Hover-Logik aufbereiten
        hover_data_instruction = "NUTZE FÜR HOVER-EFFEKTE DIESE LINKS:\n"
        for c in st.session_state.my_cards:
            hover_data_instruction += f"- {c['name']}: {c['image_uris']['normal']}\n"

        card_info = [f"CARD: {c['name']}\nTEXT: {c.get('oracle_text')}" for c in st.session_state.my_cards]
        rules_ctx = get_rules_context(prompt, [c['name'] for c in st.session_state.my_cards], st.session_state.rules_lines)
        
        sys_msg = f"""Du bist Monster Magic Mastermind.
{SYSTEM_GUIDELINES}
{hover_data_instruction}
        PRIORITÄT: 1. SPEZIAL: {SPECIAL_CASES} | 2. RULINGS: {card_info} | 3. RULES: {rules_ctx}
        VOKABULAR: {MTG_VOCABULARY}
        """

        full_messages = [{"role": "system", "content": sys_msg}] + st.session_state.messages

        def stream_generator():
            response = client.chat.completions.create(model="deepseek-chat", messages=full_messages, stream=True)
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        # Streaming-Antwort anzeigen
        full_response = st.write_stream(stream_generator())
        st.session_state.messages.append({"role": "assistant", "content": full_response})