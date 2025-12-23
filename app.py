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

# 2. CONFIG & SECRETS
if "DEEPSEEK_API_KEY" in st.secrets:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
else:
    api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 3. SESSION STATE
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

# CHAT VERLAUF ANZEIGEN
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# CHAT EINGABE & STREAMING
if prompt := st.chat_input("Deine Regelfrage an den Mastermind..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. Wir bauen die Link-Liste direkt aus den API-Daten (scryfall_uri)
        link_reference = ""
        for c in st.session_state.my_cards:
            name = c['name']
            # Wir nehmen die URI direkt aus dem Scryfall-Datensatz
            actual_url = c.get('scryfall_uri')
            if actual_url:
                link_reference += f"- {name}: {actual_url}\n"

        card_info = []
        active_special = ""
        for c in st.session_state.my_cards:
            if c['name'] in SPECIAL_CASES:
                active_special += f"\n!!! SPEZIALREGEL FÜR {c['name']}: {SPECIAL_CASES[c['name']]}\n"
            r = get_scryfall_rulings(c['id'])
            card_info.append(f"CARD: {c['name']}\nTEXT: {c.get('oracle_text')}\nRULINGS: {r}")

        rules_ctx = get_rules_context(prompt, [c['name'] for c in st.session_state.my_cards], st.session_state.rules_lines)
        
        # 2. Wir sagen der KI: Nutze NUR diese Links!
        sys_msg = f"""Du bist Monster Magic Mastermind.
        {SYSTEM_GUIDELINES}

        VERLINKUNGS-PFLICHT:
        Nutze für JEDE genannte Karte aus der Liste unten das Format: [Kartenname](URL)
        Verwende EXAKT die URLs, die hier stehen. Erfinde niemals eigene URLs!

        DEINE LINK-DATENBANK:
        {link_reference}

        KONTEXT: {active_special} | {card_info} | RULES: {rules_ctx}
        """

        def stream_generator():
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        full_response = st.write_stream(stream_generator())
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        sys_msg = f"""Du bist Monster Magic Mastermind.
{SYSTEM_GUIDELINES}

VERLINKUNG:
Wenn du eine Karte aus der folgenden Liste nennst, verlinke sie IMMER so: [KARTENNAME](URL)
KARTEN-LISTE:
{links_for_ai}

PRIORITÄT: 1. SPEZIALREGELN: {active_special} | 2. RULINGS/TEXT: {card_info} | 3. REGELN: {rules_ctx}
VOKABULAR: {MTG_VOCABULARY}
"""

        def stream_generator():
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        full_response = st.write_stream(stream_generator())
        st.session_state.messages.append({"role": "assistant", "content": full_response})
