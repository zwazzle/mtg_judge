import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
from streamlit_searchbox import st_searchbox

# --- CONFIG & SECRETS ---
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# --- TERMINOLOGIE DATENBANK ---
MTG_VOCABULARY = """
NUTZE ZWINGEND DIESE OFFIZIELLEN DEUTSCHEN BEGRIFFE:
Deathtouch -> Todesberührung; Defender -> Verteidiger; Double Strike -> Doppelschlag
Enchant -> Verzaubern; Equip -> Ausrüsten; First Strike -> Erstschlag
Flash -> Aufblitzen; Flying -> Flugfähigkeit; Haste -> Eile
Hexproof -> Fluchsicher; Indestructible -> Unzerstörbar; Lifelink -> Lebensverknüpfung
Menace -> Bedrohlichkeit; Reach -> Reichweite; Trample -> Trampelschaden
Vigilance -> Wachsamkeit; Ward -> Beschneidung; Attach -> Anlegen
Counter (Spell) -> Neutralisieren; Counter (+1/+1) -> Marke; Exile -> Ins Exil schicken
Fight -> Kämpfen; Mill -> Millen; Sacrifice -> Opfern; Scry -> Hellsicht
Surveil -> Überwachen; Tap / Untap -> Tappen / Enttappen; Battlefield -> Spielfeld
Graveyard -> Friedhof; Library -> Bibliothek; Stack -> Stapel
Instant -> Spontanzauber; Sorcery -> Hexerei; Creature -> Kreatur
Enchantment -> Verzauberung; Artifact -> Artefakt; Dredge -> Ausgraben
Kicker -> Bonus; Convoke -> Einberufen; Prowess -> Bravour
Phasing -> Instabilität; Cascade -> Kaskade; Delve -> Wühlen; Cycling -> Umwandlung
"""

# --- SESSION STATE INITIALISIERUNG ---
if 'my_cards' not in st.session_state:
    st.session_state.my_cards = []
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- FUNKTIONEN ---
def search_scryfall(searchterm: str):
    if len(searchterm) < 3: return []
    res = requests.get(f"https://api.scryfall.com/cards/named?autocomplete={searchterm}")
    if res.status_code != 200:
        res = requests.get(f"https://api.scryfall.com/cards/autocomplete?q={searchterm}")
    return res.json().get("data", []) if res.status_code == 200 else []

def get_rules_context(question, cards):
    search_terms = question.split() + [c['name'] for c in cards]
    found_lines = []
    try:
        with open("rules.txt", "r", encoding="utf-8") as f:
            all_rules = f.readlines()
        for line in all_rules:
            if any(term.lower() in line.lower() for term in search_terms if len(term) > 3):
                found_lines.append(line.strip())
        return "\n".join(found_lines[:15])
    except: return "Regelwerk nicht verfügbar."

# --- UI SETUP ---
st.set_page_config(page_title="MTG AI Judge Chat", layout="wide")
st.title("🧙‍♂️ MTG Judge Chat")

# --- TEIL 1: KARTEN-MANAGEMENT (AUTO-ADD & AUTO-RESET) ---
with st.expander("🎴 Karten-Auswahl verwalten", expanded=True):
    # Searchbox mit fixem Key für das Reset-Handling
    search_key = "card_search_input"
    selected_value = st_searchbox(
        search_scryfall, 
        key=search_key, 
        placeholder="Karte suchen und zum Hinzufügen anklicken..."
    )
    
    if selected_value:
        if selected_value not in [c['name'] for c in st.session_state.my_cards]:
            res = requests.get(f"https://api.scryfall.com/cards/named?exact={selected_value}")
            if res.status_code == 200:
                st.session_state.my_cards.append(res.json())
                
                # DER FIX: Statt auf None zu setzen, löschen wir den Key komplett.
                # 'del' entfernt den State, sodass die Box beim Rerun wieder jungfräulich ist.
                if search_key in st.session_state:
                    del st.session_state[search_key]
                
                st.rerun()
    # Galerie der gewählten Karten
    if st.session_state.my_cards:
        cols = st.columns(6)
        for i, card in enumerate(st.session_state.my_cards):
            with cols[i % 6]:
                st.image(card['image_uris']['normal'], width=150)
                if st.button("Löschen", key=f"del_{i}"):
                    st.session_state.my_cards.pop(i)
                    st.rerun()

st.divider()

# --- TEIL 2: CHAT-VERLAUF ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- TEIL 3: CHAT-EINGABE & KI ---
if prompt := st.chat_input("Stell dem Judge eine Frage zur Interaktion..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Judge überlegt..."):
            card_context = "\n".join([f"Name: {c['name']}\nText: {c.get('oracle_text')}" for c in st.session_state.my_cards])
            rules_context = get_rules_context(prompt, st.session_state.my_cards)
            
            system_instruction = f"""Du bist ein MTG Judge. Analysiere diese Situation:
            
            WICHTIGE TERMINOLOGIE (DEUTSCH):
            {MTG_VOCABULARY}
            
            KARTEN IM SPIEL:
            {card_context}
            
            RELEVANTE REGELN AUS DEM REGELBUCH:
            {rules_context}
            
            DEINE ANTWORT-STRUKTUR:
            1. Beginne mit einer Kurzfassung der richtigen Antwort (das "Urteil").
            2. Erkläre dann klar verständlich und Schritt für Schritt, warum das die richtige Antwort ist.
            3. Fasse dich kurz: Verständlichkeit geht über Ausführlichkeit.
            4. Nenne zwingend die relevanten Stellen/Nummern aus dem Regelbuch (Comprehensive Rules).
            5. FORMATIERUNG: Schreibe wichtige Begriffe, Kartennamen und Kernaussagen **fett**, um die Lesbarkeit zu verbessern.
            6. SPRACHE: Antworte auf Deutsch. Nutze für Keywords zwingend die oben genannte Terminologie."""

            messages_to_send = [{"role": "system", "content": system_instruction}] + \
                               [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages_to_send
                )
                full_response = response.choices[0].message.content
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Fehler bei der KI-Anfrage: {e}")