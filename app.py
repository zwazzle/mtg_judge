import streamlit as st
from config import AppConfig
from ui_components import UIComponents
from chat_handler import ChatHandler
from card_manager import CardManager

def main():
    """Hauptfunktion der MTG Judge App"""
    
    # 1. Seitenkonfiguration
    AppConfig.setup_page()
    
    # 2. Session State initialisieren
    AppConfig.initialize_session_state()
    
    # 3. UI-Komponenten initialisieren
    ui = UIComponents()
    card_mgr = CardManager()
    chat_handler = ChatHandler()
    
    # 4. Header rendern
    ui.render_header()
    
    # 5. Karten-Management-Bereich
    with st.expander("🎴 Karten-Auswahl verwalten", expanded=True):
        card_mgr.render_card_search()
        card_mgr.render_card_grid()
    
    # 6. Chat-Verlauf anzeigen
    ui.render_chat_history()
    
    # 7. Chat-Eingabe verarbeiten
    if prompt := st.chat_input("Deine Regelfrage an den Mastermind..."):
        chat_handler.handle_user_message(prompt)

if __name__ == "__main__":
    main()
