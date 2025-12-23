import streamlit as st
import os

class AppConfig:
    """Zentrale Konfigurationsklasse für die App"""
    
    # App-Metadaten
    PAGE_TITLE = "Monster Magic Mastermind"
    PAGE_ICON = "🧙‍♂️"
    LAYOUT = "wide"
    
    # API-Konfiguration
    API_BASE_URL = "https://api.deepseek.com"
    MODEL_NAME = "deepseek-chat"
    
    # Scryfall API
    SCRYFALL_BASE_URL = "https://api.scryfall.com"
    
    # Cache-Einstellungen
    CACHE_TTL = 3600  # 1 Stunde
    
    @staticmethod
    def setup_page():
        """Setzt die Streamlit-Seitenkonfiguration"""
        st.set_page_config(
            page_title=AppConfig.PAGE_TITLE,
            page_icon=AppConfig.PAGE_ICON,
            layout=AppConfig.LAYOUT
        )
    
    @staticmethod
    def get_api_key():
        """Holt den API-Key aus Secrets oder Umgebungsvariablen"""
        if "DEEPSEEK_API_KEY" in st.secrets:
            return st.secrets["DEEPSEEK_API_KEY"]
        return os.getenv("DEEPSEEK_API_KEY")
    
    @staticmethod
    def initialize_session_state():
        """Initialisiert alle Session State Variablen"""
        
        # Regeln laden
        if "rules_lines" not in st.session_state:
            try:
                with open("rules.txt", "r", encoding="utf-8") as f:
                    st.session_state.rules_lines = f.readlines()
            except FileNotFoundError:
                st.session_state.rules_lines = []
                st.warning("⚠️ rules.txt nicht gefunden. Regelsuche ist eingeschränkt.")
        
        # Karten-Liste
        if 'my_cards' not in st.session_state:
            st.session_state.my_cards = []
        
        # Chat-Verlauf
        if 'messages' not in st.session_state:
            st.session_state.messages = []
