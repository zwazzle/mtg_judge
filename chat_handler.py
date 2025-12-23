import streamlit as st
from openai import OpenAI
from config import AppConfig
from card_manager import CardManager
from mtg_logic import MTGLogic
from database import SYSTEM_GUIDELINES, SPECIAL_CASES

class ChatHandler:
    """Verwaltet die Chat-Funktionalität und KI-Interaktion"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=AppConfig.get_api_key(),
            base_url=AppConfig.API_BASE_URL
        )
        self.card_manager = CardManager()
        self.mtg_logic = MTGLogic()
    
    def build_system_message(self, prompt):
        """Baut die System-Nachricht für die KI"""
        
        # Karten-Links für Verlinkung
        card_links = self.card_manager.get_card_links()
        
        # Karten-Informationen (Oracle Text + Rulings)
        card_info_list = []
        special_rules = []
        
        for card in st.session_state.my_cards:
            card_name = card['name']
            
            # Spezialregeln prüfen
            if card_name in SPECIAL_CASES:
                special_rules.append(
                    f"\n!!! SPEZIALREGEL FÜR {card_name}:\n{SPECIAL_CASES[card_name]}\n"
                )
            
            # Oracle Text und Rulings
            oracle_text = card.get('oracle_text', 'Kein Text verfügbar')
            rulings = self.mtg_logic.get_scryfall_rulings(card['id'])
            
            card_info_list.append(
                f"CARD: {card_name}\n"
                f"TEXT: {oracle_text}\n"
                f"RULINGS: {rulings}"
            )
        
        card_info = "\n\n".join(card_info_list)
        active_special = "\n".join(special_rules)
        
        # Regelkontext aus rules.txt
        card_names = self.card_manager.get_card_names()
        rules_context = self.mtg_logic.get_rules_context(
            prompt, 
            card_names, 
            st.session_state.rules_lines
        )
        
        # System-Prompt zusammenbauen
        system_message = f"""Du bist Monster Magic Mastermind.

{SYSTEM_GUIDELINES}

VERLINKUNGS-PFLICHT:
Nutze für JEDE genannte Karte aus der Liste unten das Format: [Kartenname](URL)
Verwende EXAKT die URLs, die hier stehen. Erfinde niemals eigene URLs!

DEINE LINK-DATENBANK:
{card_links}

PRIORITÄT:
1. SPEZIALREGELN (höchste Priorität): {active_special}
2. KARTEN-DETAILS: {card_info}
3. REGELKONTEXT: {rules_context}
"""
        
        return system_message
    
    def stream_ai_response(self, system_message):
        """Streamt die Antwort der KI"""
        
        messages = [
            {"role": "system", "content": system_message}
        ] + st.session_state.messages
        
        try:
            response = self.client.chat.completions.create(
                model=AppConfig.MODEL_NAME,
                messages=messages,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"\n\n❌ Fehler bei der KI-Anfrage: {str(e)}"
    
    def handle_user_message(self, prompt):
        """Verarbeitet eine Benutzernachricht"""
        
        # Nachricht zum Verlauf hinzufügen
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Nachricht anzeigen
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # KI-Antwort generieren
        with st.chat_message("assistant"):
            system_message = self.build_system_message(prompt)
            
            # Streaming der Antwort
            full_response = st.write_stream(
                self.stream_ai_response(system_message)
            )
            
            # Antwort zum Verlauf hinzufügen
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })
