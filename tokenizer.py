# local_tokenizer.py

import spacy

# Загружаем модель для русского языка
try:
    nlp = spacy.load("ru_core_news_sm")
except OSError:
    # Если модель не установлена — выводим инструкцию
    raise RuntimeError(
        "Модель spaCy 'ru_core_news_sm' не установлена. "
        "Установите её командой:\n"
        "python -m spacy download ru_core_news_sm"
    )

def spacy_tokenizer(text):
    """
    Токенизирует и нормализует входной текст. Возвращает список токенов без стоп-слов и пунктуации.
    """
    doc = nlp(text.lower())
    return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]

