import streamlit as st
import requests
from streamlit_searchbox import st_searchbox
from config import AppConfig
from ui_components import UIComponents

class CardManager:
    """Verwaltet das Hinzufügen, Anzeigen und Löschen von Karten"""
    
    def __init__(self):
        self.ui = UIComponents()
        self.search_key = "card_search"
    
    def search_scryfall(self, searchterm: str):
        """Sucht Karten auf Scryfall (Autocomplete)"""
        if len(searchterm) < 3:
            return []
        
        try:
            url = f"{AppConfig.SCRYFALL_BASE_URL}/cards/autocomplete?q={searchterm}"
            res = requests.get(url, timeout=5)
            
            if res.status_code == 200:
                return res.json().get("data", [])
        except Exception as e:
            st.error(f"Fehler bei der Kartensuche: {e}")
            return []
        
        return []
    
    def fetch_card_details(self, card_name):
        """Holt detaillierte Karteninformationen von Scryfall"""
        try:
            url = f"{AppConfig.SCRYFALL_BASE_URL}/cards/named?exact={card_name}"
            res = requests.get(url, timeout=5)
            
            if res.status_code == 200:
                return res.json()
            else:
                st.error(f"Karte '{card_name}' nicht gefunden.")
                return None
        except Exception as e:
            st.error(f"Fehler beim Laden der Karte: {e}")
            return None
    
    def add_card(self, card_data):
        """Fügt eine Karte zur Auswahl hinzu"""
        if card_data and card_data not in st.session_state.my_cards:
            # Prüfen ob Karte schon existiert (nach Name)
            if card_data['name'] not in [c['name'] for c in st.session_state.my_cards]:
                st.session_state.my_cards.append(card_data)
                return True
        return False
    
    def remove_card(self, index):
        """Entfernt eine Karte aus der Auswahl"""
        if 0 <= index < len(st.session_state.my_cards):
            st.session_state.my_cards.pop(index)
            return True
        return False
    
    def render_card_search(self):
        """Rendert die Kartensuche"""
        selected = st_searchbox(
            self.search_scryfall,
            key=self.search_key,
            placeholder="Kartenname eingeben..."
        )
        
        if selected:
            card_data = self.fetch_card_details(selected)
            
            if card_data and self.add_card(card_data):
                # Search-Box zurücksetzen
                if self.search_key in st.session_state:
                    del st.session_state[self.search_key]
                st.rerun()
    
    def render_card_grid(self, columns=6):
        """Rendert das Karten-Grid mit allen ausgewählten Karten"""
        if not st.session_state.my_cards:
            st.info("Noch keine Karten ausgewählt. Suche oben nach Karten!")
            return
        
        cols = st.columns(columns)
        
        for i, card in enumerate(st.session_state.my_cards):
            with cols[i % columns]:
                self.ui.render_card_image(card, width=150)
                
                # Kartenname unter dem Bild
                st.caption(card.get('name', 'Unbekannt'))
                
                # Löschen-Button
                if st.button("🗑️ Löschen", key=f"del_{i}"):
                    self.remove_card(i)
                    st.rerun()
    
    def get_card_names(self):
        """Gibt eine Liste aller Kartennamen zurück"""
        return [card['name'] for card in st.session_state.my_cards]
    
    def get_card_links(self):
        """Erstellt eine formatierte Liste mit Karten-Links für die KI"""
        links = []
        for card in st.session_state.my_cards:
            name = card['name']
            url = card.get('scryfall_uri', '')
            if url:
                links.append(f"- {name}: {url}")
        
        return "\n".join(links) if links else "Keine Karten ausgewählt."
