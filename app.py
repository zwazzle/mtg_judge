import streamlit as st
import os
import requests
from openai import OpenAI
from streamlit_searchbox import st_searchbox

# Eigene Module importieren
from database import MTG_VOCABULARY, SPECIAL_CASES, SYSTEM_GUIDELINES
from mtg_logic import get_scryfall_rulings, get_rules_context, search_scryfall

# 1. PAGE CONFIG
st.set_page_config(page_title="Monster Magic Mastermind", page_icon="🧙‍♂️", layout="wide")

# 2. VERBESSERTES CSS FÜR HOVER
# Wir nutzen Inline-Styles für das Bild, da CSS-Variablen im Stream schwer zu greifen sind
st.markdown("""
    <style>
    .card-hover {
        color: #ff4b4b !important;
        text-decoration: underline;
        cursor: help;
        position: relative;
        font-weight: bold;
    }
    .card-hover .tooltip-img {
        display: none;
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        width: 220px;
        z-index: 1000;
        border-radius: 10px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.8);
    }
    .card-hover:hover .tooltip-img {
        display: block;
    }
    </style>
""", unsafe_allow_html=True)

# 3. CONFIG
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
    except: st.session_state.rules_lines = []

if 'my_cards' not in st.session_state: st.session_state.my_cards = []
if 'messages' not in st.session_state: st.session_state.messages = []

# --- UI ---
st.title("🧙‍♂️ Monster Magic Mastermind")

with st.expander("🎴 Karten-Auswahl verwalten", expanded=True):
    search_key = "card_search"
    selected = st_searchbox(search_scryfall, key=search_key)
    if selected:
        res = requests.get(f"https://api.scryfall.com/cards/named?exact={selected}")
        if res.status_code == 200:
            st.session_state.my_cards.append(res.json())
            st.rerun()

    cols = st.columns(6)
    for i, card in enumerate(st.session_state.my_cards):
        with cols[i % 6]:
            st.image(card['image_uris']['normal'], width=150)
            if st.button("Löschen", key=f"del_{i}"):
                st.session_state.my_cards.pop(i)
                st.rerun()

# CHAT ANZEIGE
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"], unsafe_allow_html=True)

# CHAT EINGABE & STREAMING
if prompt := st.chat_input("Deine Regelfrage..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        # Bild-URLs für die KI vorbereiten
        hover_instruction = "NUTZE FÜR KARTEN DIESES HTML: <span class='card-hover'>NAME<img class='tooltip-img' src='URL'></span>\n"
        for c in st.session_state.my_cards:
            hover_instruction += f"- {c['name']}: {c['image_uris']['normal']}\n"

        card_info = [f"CARD: {c['name']}\nTEXT: {c.get('oracle_text')}" for c in st.session_state.my_cards]
        rules_ctx = get_rules_context(prompt, [c['name'] for c in st.session_state.my_cards], st.session_state.rules_lines)
        
        sys_msg = f"""Du bist Monster Magic Mastermind. 
        {SYSTEM_GUIDELINES}
        {hover_instruction}
        VOKABULAR: {MTG_VOCABULARY}
        KONTEXT: {card_info} | RULES: {rules_ctx}"""

        def stream_generator():
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        # WICHTIG: Damit das Streaming HTML erlaubt, nutzen wir einen Container
        placeholder = st.empty()
        full_response = ""
        
        for chunk in stream_generator():
            full_response += chunk
            # Wir rendern den Text bei jedem Schritt neu als HTML
            placeholder.write(full_response, unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})