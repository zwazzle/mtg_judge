import streamlit as st
from config import AppConfig

class UIComponents:
    """Klasse für alle UI-Komponenten"""
    
    def __init__(self):
        self.config = AppConfig()
    
    def render_header(self):
        """Rendert den Header der App"""
        st.title(f"{AppConfig.PAGE_ICON} {AppConfig.PAGE_TITLE}")
        
        # Optional: Info-Box oder Anleitung
        # st.info("💡 Wähle Karten aus und stelle Regelfragen!")
    
    def render_chat_history(self):
        """Zeigt den gesamten Chat-Verlauf an"""
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    def render_card_image(self, card, width=150):
        """Rendert ein einzelnes Kartenbild"""
        if 'image_uris' in card:
            st.image(card['image_uris']['normal'], width=width)
        else:
            st.info(f"🃏 {card.get('name', 'Unbekannt')}")
    
    def render_error(self, message):
        """Zeigt eine Fehlermeldung an"""
        st.error(f"❌ {message}")
    
    def render_success(self, message):
        """Zeigt eine Erfolgsmeldung an"""
        st.success(f"✅ {message}")
    
    def render_info(self, message):
        """Zeigt eine Info-Meldung an"""
        st.info(f"ℹ️ {message}")
