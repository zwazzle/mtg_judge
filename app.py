import streamlit as st
import os
import requests
from openai import OpenAI
from streamlit_searchbox import st_searchbox

# Eigene Module importieren
from database import MTG_VOCABULARY, SPECIAL_CASES, SYSTEM_GUIDELINES
from mtg_logic import get_scryfall_rulings, get_rules_context, search_scryfall

# --- CONFIG & SECRETS (GITHUB VERSION) ---
# Streamlit Cloud nutzt st.secrets anstatt einer .env Datei
if "DEEPSEEK_API_KEY" in st.secrets:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
else:
    api_key = os.getenv("DEEPSEEK_API_KEY") # Fallback für lokale Tests

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

if "rules_lines" not in st.session_state:
    try:
        # Achte darauf, dass rules.txt auch im GitHub Repository liegt!
        with open("rules.txt", "r", encoding="utf-8") as f:
            st.session_state.rules_lines = f.readlines()
    except FileNotFoundError:
        st.session_state.rules_lines = []

if 'my_cards' not in st.session_state: st.session_state.my_cards = []
if 'messages' not in st.session_state: st.session_state.messages = []

# --- UI ---
st.set_page_config(page_title="Monster Magic Mastermind", layout="wide")
st.title("🧙‍♂️ MTG Judge Chat")

# Karten-Management
with st.expander("🎴 Karten-Auswahl", expanded=True):
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

# Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Deine Regelfrage..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Judge analysiert..."):
            card_info = []
            active_special = ""
            for c in st.session_state.my_cards:
                if c['name'] in SPECIAL_CASES:
                    active_special += f"\n!!! SPEZIALREGEL FÜR {c['name']}: {SPECIAL_CASES[c['name']]}\n"
                r = get_scryfall_rulings(c['id'])
                card_info.append(f"CARD: {c['name']}\nTEXT: {c.get('oracle_text')}\nOFFICIAL RULINGS:\n{r}")

            rules_ctx = get_rules_context(prompt, [c['name'] for c in st.session_state.my_cards], st.session_state.rules_lines)
            
            sys_msg = f"""Du bist ein MTG Regelexperte. Benutze immer die englischen Namen der Karten.
{SYSTEM_GUIDELINES}
            PRIORITÄT: 1. SPEZIALREGELN: {active_special} | 2. RULINGS/TEXT: {card_info} | 3. REGELN: {rules_ctx}
            VOKABULAR: {MTG_VOCABULARY}
            STRUKTUR: Urteil (Fett), Erklärung, Regel-Nummern."""

            full_messages = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            
            try:
                response = client.chat.completions.create(model="deepseek-chat", messages=full_messages)
                ans = response.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            except Exception as e:
                st.error(f"Fehler bei der KI-Anfrage: {e}")