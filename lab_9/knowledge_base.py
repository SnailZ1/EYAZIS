# Domain Knowledge Base
# Medical and Art terminology relationships for semantic linking

MEDICAL_RU = {
    "диагностика": ["обследование", "анализ", "исследование"],
    "лечение": ["терапия", "медикаментозное", "хирургическое"],
    "симптом": ["признак", "проявление", "синдром"],
    "заболевание": ["болезнь", "патология", "недуг"],
    "пациент": ["больной", "человек"],
    "врач": ["доктор", "специалист", "медик"],
    "препарат": ["лекарство", "медикамент", "средство"],
    "клиника": ["больница", "стационар", "госпиталь"],
    "профилактика": ["предупреждение", "предотвращение"],
    "иммунитет": ["защита", "сопротивляемость"],
    "вакцина": ["прививка", "иммунизация"],
    "инфекция": ["заражение", "воспаление"],
    "хирургия": ["операция", "вмешательство"],
    "реабилитация": ["восстановление", "выздоровление"]
}

MEDICAL_EN = {
    "diagnosis": ["examination", "analysis", "investigation"],
    "treatment": ["therapy", "medication", "surgery"],
    "symptom": ["sign", "manifestation", "syndrome"],
    "disease": ["illness", "pathology", "condition"],
    "patient": ["person", "individual"],
    "doctor": ["physician", "specialist", "practitioner"],
    "drug": ["medicine", "medication", "pharmaceutical"],
    "clinic": ["hospital", "facility", "center"],
    "prevention": ["prophylaxis", "precaution"],
    "immunity": ["resistance", "defense"],
    "vaccine": ["immunization", "inoculation"],
    "infection": ["contamination", "inflammation"],
    "surgery": ["operation", "procedure"],
    "rehabilitation": ["recovery", "restoration"]
}

ART_RU = {
    "живопись": ["картина", "полотно", "изображение"],
    "художник": ["живописец", "мастер", "автор"],
    "композиция": ["построение", "структура", "расположение"],
    "колорит": ["цвет", "палитра", "краски"],
    "техника": ["манера", "метод", "приём"],
    "стиль": ["направление", "манера", "школа"],
    "выставка": ["экспозиция", "показ", "демонстрация"],
    "музей": ["галерея", "собрание", "коллекция"],
    "шедевр": ["произведение", "творение", "работа"],
    "критика": ["анализ", "оценка", "рецензия"],
    "искусство": ["творчество", "художество"],
    "эстетика": ["красота", "гармония"],
    "символизм": ["образность", "метафоричность"],
    "реализм": ["натурализм", "жизненность"]
}

ART_EN = {
    "painting": ["picture", "canvas", "artwork"],
    "artist": ["painter", "master", "creator"],
    "composition": ["structure", "arrangement", "layout"],
    "color": ["palette", "hue", "tone"],
    "technique": ["method", "approach", "style"],
    "style": ["manner", "school", "movement"],
    "exhibition": ["show", "display", "exposition"],
    "museum": ["gallery", "collection"],
    "masterpiece": ["work", "creation", "piece"],
    "criticism": ["analysis", "review", "critique"],
    "art": ["artwork", "creative work"],
    "aesthetics": ["beauty", "harmony"],
    "symbolism": ["imagery", "metaphor"],
    "realism": ["naturalism", "verisimilitude"]
}

KNOWLEDGE_BASE = {
    "medical": {"ru": MEDICAL_RU, "en": MEDICAL_EN},
    "art": {"ru": ART_RU, "en": ART_EN}
}
