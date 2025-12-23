# --- OFFIZIELLE MTG TERMINOLOGIE (DEUTSCH) ---
# Diese Liste sorgt dafür, dass die KI nicht zwischen Englisch und Deutsch halluziniert.
MTG_VOCABULARY = """
Das sind die deutschen Übersetzungen der englischen Keywords:
- Deathtouch -> Todesberührung
- Defender -> Verteidiger
- Double Strike -> Doppelschlag
- Enchant -> Verzaubern
- Equip -> Ausrüsten
- First Strike -> Erstschlag
- Flash -> Aufblitzen
- Flying -> Flugfähigkeit
- Haste -> Eile
- Hexproof -> Fluchsicher
- Indestructible -> Unzerstörbar
- Lifelink -> Lebensverknüpfung
- Menace -> Bedrohlichkeit
- Reach -> Reichweite
- Trample -> Trampelschaden
- Vigilance -> Wachsamkeit
- Ward -> Beschneidung
- Attach -> Anlegen
- Counter (Spell) -> Neutralisieren
- Counter (+1/+1) -> Marke
- Exile -> Ins Exil schicken
- Fight -> Kämpfen
- Mill -> Millen
- Sacrifice -> Opfern
- Scry -> Hellsicht
- Surveil -> Überwachen
- Tap / Untap -> Tappen / Enttappen
- Battlefield -> Spielfeld
- Graveyard -> Friedhof
- Library -> Bibliothek
- Stack -> Stapel
- Instant -> Spontanzauber
- Sorcery -> Hexerei
- Creature -> Kreatur
- Enchantment -> Verzauberung
- Artifact -> Artefakt
- Dredge -> Ausgraben
- Kicker -> Bonus
- Convoke -> Einberufen
- Prowess -> Bravour
- Phasing -> Instabilität
- Cascade -> Kaskade
- Delve -> Wühlen
- Cycling -> Umwandlung
"""

# --- SPEZIAL-DATENBANK FÜR KOMPLIZIERTE KARTEN (EDGE CASES) ---
# Hier fügst du Karten hinzu, bei denen die KI oft Fehler macht.
# Der Bot liest diese Informationen mit höchster Priorität.

SPECIAL_CASES = {
    "Omo, Queen of Vesuva": (
        "Omos Fähigkeit ist eine statische Fähigkeit, die auf dem Spielfeld existieren muss. "
        "Sobald Omo das Spielfeld verlässt, verlieren die 'Everything Counter' (Alles-Marken) ihre Wirkung. "
        "Die Marken bleiben zwar physisch auf den Karten liegen, aber die Länder/Kreaturen verlieren sofort "
        "alle zusätzlichen Typen, die Omo ihnen verliehen hat (Regel 611.3b)."
    ),
    
    "Blood Moon": (
        "Nicht-Standardländer werden zu Gebirgen. Wichtig: Sie verlieren alle ihre gedruckten Fähigkeiten "
        "und erhalten nur die Fähigkeit '{T}: Erzeuge {R}'. Sie behalten jedoch ihren Namen und ihren "
        "Status (z.B. bleibt ein legendäres Land legendär)."
    ),
    
    "Grist, the Hunger Tide": (
        "Grist ist in jeder Zone außer dem Spielfeld eine 1/1 Insekt-Kreatur. "
        "Das bedeutet, man kann Grist mit Karten wie 'Chord of Calling' suchen oder mit 'Raise Dead' "
        "vom Friedhof auf die Hand holen. Nur auf dem Spielfeld ist sie ein Planeswalker."
    ),
    
    "Yedora, Grave Gardener": (
        "Kreaturen, die unter Yedora als Wald zurückkehren, sind verdeckte Karten (Face-down). "
        "Sie sind NUR Länder vom Typ Wald. Sie haben keine Namen, keine Manakosten und keine Kreaturentypen. "
        "Sie sind keine Kreaturen-Land-Hybride, sondern reine Länder."
    ),
    
    "Pithing Needle": (
        "Die Nadel verhindert nur AKTIVIERTE Fähigkeiten (Format: Kosten : Effekt). "
        "Sie verhindert KEINE statischen Fähigkeiten (wie 'Kreaturen erhalten +1/+1') "
        "und KEINE ausgelösten Fähigkeiten (Trigger, die mit 'Wann', 'Immer wenn' oder 'Zu Beginn' starten)."
    ),

    "Humility": (
        "Humility setzt alle Kreaturen auf 1/1 und entfernt alle Fähigkeiten. "
        "Dies ist ein Layer-6-Effekt (Fähigkeiten) und ein Layer-7b-Effekt (PT). "
        "Wichtig bei Interaktionen mit Karten wie 'Magus of the Moon': Die Reihenfolge (Timestamp) entscheidet."
    ),
    
    "Obeka, Brute Chronologist": (
        "Das Beenden des Zuges entfernt alle Zauber und Fähigkeiten vom Stapel. "
        "Effekte, die 'bis zum Ende des Zuges' (until end of turn) dauern, enden trotzdem erst in der "
        "Cleanup-Phase. Effekte, die 'zu Beginn des nächsten Endsegments' triggern, "
        "werden umgangen, wenn man den Zug davor beendet."
    )
}

# --- HILFSTEXTE FÜR DEN JUDGE ---
SYSTEM_GUIDELINES = """
1. Beginne immer mit einem netten Kompliment über die knifflige Frage! Sei wie ein Freund, der sich sehr gut mit dem Regelwerk auskennt und immer gerne darüber reden mag.
2. Beantworte die Frage mit einer kurzen klaren Antwort.
3. Erkläre gut verständlich und klar, wie du auf deine Antwort gekommen bist. Halte dich kurz und prägnant.
4. Nenne die Regelnummern der 'Comprehensive Rules' (CR), wenn möglich, und zitiere den relevanten Regeltext, falls er Klarheit schafft.
5. Erkläre das Konzept der 'Layers', falls es um Typ-Änderungen oder Status-Änderungen geht.
6. Stelle eine Rückfrage, ob du noch weitere Unklarheiten zur Ursprungsfrage beantworten kannst, oder ob etwas unklar geblieben ist. 
7. Kartennamen, die du nennst, IMMMER auf Englisch! 
"""