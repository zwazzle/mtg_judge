import streamlit as st
import requests

@st.cache_data(ttl=3600)
def get_scryfall_rulings(card_id):
    """Holt die offiziellen Oracle Rulings von Scryfall."""
    try:
        res = requests.get(f"https://api.scryfall.com/cards/{card_id}/rulings")
        if res.status_code == 200:
            rulings = res.json().get("data", [])
            return "\n".join([f"- {r['comment']}" for r in rulings]) if rulings else "Keine Rulings vorhanden."
    except Exception as e:
        return f"Fehler beim Laden der Rulings: {e}"
    return ""

@st.cache_data
def get_rules_context(question, card_names, _rules_lines):
    """Sucht relevante Passagen aus der rules.txt."""
    search_terms = question.split() + list(card_names)
    found = [line.strip() for line in _rules_lines 
             if any(term.lower() in line.lower() for term in search_terms if len(term) > 3)]
    return "\n".join(found[:30])

def search_scryfall(searchterm: str):
    """Wird von der Searchbox für die Autovervollständigung genutzt."""
    if len(searchterm) < 3: 
        return []
    try:
        # Wir nutzen hier den Autocomplete-Endpunkt von Scryfall
        res = requests.get(f"https://api.scryfall.com/cards/autocomplete?q={searchterm}")
        if res.status_code == 200:
            return res.json().get("data", [])
    except Exception:
        return []
    return []