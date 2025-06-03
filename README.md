# NLP-сервер для голосового помощника 

## Описание

Реализует базовый NLP-сервер для классификации пользовательских команд и извлечения сущностей из текста на русском языке.
Поддерживается распознавание команд с порогом уверенности.


---

## Требования

- Python 3.8+
- pip
- [spaCy](https://spacy.io/) и русская модель `ru_core_news_sm`
- transformers
- torch
- flask
- pymorphy2
- pandas

---

## Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/a6p/deepprokhor-lite.git
cd deepprokhor-lite
```
2. Создайте и активируйте виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
```
3. Установите зависимости:

```bash
pip install -r requirements.txt
python -m spacy download ru_core_news_sm
```
## Обучение

Перед запуском надо дообучить BERT модель, без этого сервер не запустится.
Датасет, который я использовал в data.csv.

Для дообучения модели:

```bash
pip install transformers[torch] scikit-learn
python train_finetune.py
```
## Запуск сервера

```bash
python server.py
```
Сервер будет доступен по адресу: http://0.0.0.0:8080

## Использование API

POST /nlp

Тело запроса (JSON):

{
  "text": "установи будильник на утро"
}

Пример ответа:

{
  "entities": {
    "alarm": {
      "date": "2025-06-03",
      "period": "утро",
      "time": "07:00"
    },
    "application": null,
    "city": null,
    "device": null,
    "room": null,
    "value": null,
    "video_title": null,
    "weather": {
      "date": null,
      "period": null
    }
  },
  "intent": "set_alarm",
  "intent_score": 0.545,
  "text": "установи будильник на утро"
}


Для проверки выполните в консоли:
```bash
curl -X POST http://localhost:8080/nlp -H "Content-Type: application/json" -d '{"text": "включи музыку"}'|jq
curl -X POST http://localhost:8080/nlp -H "Content-Type: application/json" -d '{"text": "установи будильник на завтра на 14 45"}'|jq
```

# Тесты

```bash
pip install unittest requests
python test.py
```
