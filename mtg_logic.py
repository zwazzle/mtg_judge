import streamlit as st
import requests
from config import AppConfig

class MTGLogic:
    """Enthält die MTG-spezifische Logik (Rulings, Regelsuche, etc.)"""
    
    @staticmethod
    @st.cache_data(ttl=AppConfig.CACHE_TTL)
    def get_scryfall_rulings(card_id):
        """Holt die offiziellen Oracle Rulings von Scryfall"""
        try:
            url = f"{AppConfig.SCRYFALL_BASE_URL}/cards/{card_id}/rulings"
            res = requests.get(url, timeout=5)
            
            if res.status_code == 200:
                rulings = res.json().get("data", [])
                
                if rulings:
                    return "\n".join([f"- {r['comment']}" for r in rulings])
                else:
                    return "Keine offiziellen Rulings vorhanden."
            else:
                return "Rulings konnten nicht geladen werden."
                
        except Exception as e:
            return f"Fehler beim Laden der Rulings: {e}"
    
    @staticmethod
    @st.cache_data
    def get_rules_context(question, card_names, _rules_lines):
        """Sucht relevante Passagen aus der rules.txt"""
        
        # Suchbegriffe aus Frage + Kartennamen
        search_terms = question.split() + list(card_names)
        
        # Nur Begriffe mit mehr als 3 Zeichen
        search_terms = [term for term in search_terms if len(term) > 3]
        
        # Relevante Zeilen finden
        found_lines = []
        for line in _rules_lines:
            line_lower = line.lower()
            
            # Prüfen ob irgendein Suchbegriff in der Zeile vorkommt
            if any(term.lower() in line_lower for term in search_terms):
                found_lines.append(line.strip())
        
        # Maximal 30 Zeilen zurückgeben
        relevant_rules = found_lines[:30]
        
        if relevant_rules:
            return "\n".join(relevant_rules)
        else:
            return "Keine passenden Regeln gefunden."
    
    @staticmethod
    def format_card_info(card):
        """Formatiert Karteninformationen für die Anzeige"""
        info = {
            "name": card.get("name", "Unbekannt"),
            "type": card.get("type_line", ""),
            "mana_cost": card.get("mana_cost", ""),
            "oracle_text": card.get("oracle_text", ""),
            "power": card.get("power", ""),
            "toughness": card.get("toughness", ""),
        }
        return info


# Für Backwards Compatibility - falls alte Funktionen aufgerufen werden
def get_scryfall_rulings(card_id):
    """Legacy-Funktion für Kompatibilität"""
    return MTGLogic.get_scryfall_rulings(card_id)

def get_rules_context(question, card_names, rules_lines):
    """Legacy-Funktion für Kompatibilität"""
    return MTGLogic.get_rules_context(question, card_names, rules_lines)

def search_scryfall(searchterm: str):
    """Wird von der Searchbox für die Autovervollständigung genutzt."""
    if len(searchterm) < 3: 
        return []
    try:
        res = requests.get(f"https://api.scryfall.com/cards/autocomplete?q={searchterm}")
        if res.status_code == 200:
            return res.json().get("data", [])
    except Exception:
        return []
    return []
