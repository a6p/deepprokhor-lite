from pymorphy2 import MorphAnalyzer
from datetime import datetime, timedelta
import calendar
import spacy
import re

nlp = spacy.load("ru_core_news_sm")

# Словари
WEATHER_TIME_MAP = {
    "сегодня": "today",
    "завтра": "tomorrow",
    "послезавтра": "after_tomorrow",
    "неделю": "week",
    "неделя": "week",
    "на неделе": "week",
    "на этой неделе": "this_week",
    "на следующей неделе": "next_week",
}
DAY_FORMS = {
    "понедельник": ["понедельник", "пн"],
    "вторник": ["вторник", "вт"],
    "среда": ["среда", "ср"],
    "четверг": ["четверг", "чт"],
    "пятница": ["пятница", "пт"],
    "суббота": ["суббота", "сб"],
    "воскресенье": ["воскресенье", "вс"]
}
WEEKEND_FORMS = ["выходные", "викенд", "конец недели"]
ALARM_CMDS = ["будильник", "разбуди", "подъем", "пробуждение", "напомни"]
WEATHER_CMDS = ["погода", "погоду", "прогноз", "температура", "осадки", "дождь", "снег", "град"]
TIME_PERIODS = ["утро", "день", "вечер", "ночь", "обед"]
DAYS_OF_WEEK = {
    "понедельник": 0, "вторник": 1, "среда": 2, "среду":2, "четверг": 3,
    "пятница": 4, "пятницу":4, "суббота": 5, "субботу":5, "воскресенье": 6
}
RELATIVE_DAYS = {
    "сегодня": 0, "завтра": 1, "послезавтра": 2,
    "послепослезавтра": 3, "через 3 дня": 3
}

ROOM_MAP = {
    "спальне": "спальня", "спальня": "спальня",
    "кухне": "кухня", "кухня": "кухня",
    "зале": "зал", "зал": "зал",
    "гостиной": "гостиная", "гостиная": "гостиная",
    "ванной": "ванная", "ванная": "ванная",
    "повсюду": "дом", "доме": "дом", "дом": "дом", "везде": "дом",
}

DEVICES_MAP = {
    "свет": ["свет", "лампа", "лампы", "лампочка", "лампочки"],
    "кондиционер": ["кондиционер", "кондишн", "кондишнёр"],
    "вентилятор": ["вентилятор", "вент"],
    "шторы": ["штора", "шторы", "занавески"],
    "телевизор": ["телевизор", "тв", "телик", "теле"],
}

APP_MAP = {
    "youtube": ["ютуб", "youtube", "ютюб", "ютубе"],
    "youtube music": ["ютуб музик", "ютуб музыка", "youtube music"],
    "netflix": ["нетфликс", "netflix"],
    "kinopoisk": ["кинопоиск", "кинопоиске"],
    "spotify": ["спотифай", "spotify"],
    "twitch": ["твич", "twitch"],
    "prime video": ["прайм видео", "prime video"],
    "wink": ["винк", "винке" "twitch"],
}

# Команды для управления видео
VIDEO_CMDS = ["включи", "запусти", "поставь", "покажи", "включить", "запустить", "поставить", "показать"]

morph = MorphAnalyzer()

#def normalize_day(day_str):
#    """Нормализует день недели с помощью pymorphy2"""
#    parsed = morph.parse(day_str)[0]
#    return parsed.normal_form

def normalize_city(city_raw):
    """Нормализуем название города с помощью pymorphy2"""
    words = city_raw.strip().split()
    city_words = [morph.parse(word)[0].normal_form for word in words]
    return " ".join(city_words)

def parse_datetime(text, reference_date=None):
    """Парсинг временных выражений"""
    if reference_date is None:
        reference_date = datetime.now()

    text = text.lower()
    result = {
        "date": None,
        "time": None,
        "period": None,
        "date_str": None,
    }

    # Поиск периода (утро, день, вечер, ночь)
    for period in TIME_PERIODS:
        if period in text:
            result["period"] = period

    # Поиск выходных
    weekend_match = re.search(r"\b(выходн|викенд|конец недел)\w*\b", text)
    if weekend_match:
        # Находим ближайшие выходные (субботу)
        current_weekday = reference_date.weekday()
        days_to_saturday = (5 - current_weekday) % 7 or 7
        saturday = reference_date + timedelta(days=days_to_saturday)
        result["date"] = saturday
        result["date_str"] = saturday.strftime("%Y-%m-%d")
        result["period"] = "weekend"
        return result  # Выходные имеют приоритет

    # Поиск относительных дней (сегодня, завтра)
    for day, offset in RELATIVE_DAYS.items():
        if re.search(rf"\b{re.escape(day)}\b", text):
            target_date = reference_date + timedelta(days=offset)
            result["date"] = target_date
            result["date_str"] = target_date.strftime("%Y-%m-%d")
            break

    # Поиск дней недели
    for day_ru, day_num in DAYS_OF_WEEK.items():
        if day_ru in text:
            current_weekday = reference_date.weekday()
            days_ahead = day_num - current_weekday
            if days_ahead <= 0:
                days_ahead += 7
            target_date = reference_date + timedelta(days=days_ahead)
            result["date"] = target_date
            result["date_str"] = target_date.strftime("%Y-%m-%d")
            break

    # Поиск дат (число + месяц)
    date_match = re.search(
        r"(\d{1,2})(?:\s*[-.]?\s*го)?\s*(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)?",
        text
    )
    if date_match:
        day = int(date_match.group(1))
        month_name = date_match.group(2)

        month_map = {
            "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
            "мая": 5, "июня": 6, "июля": 7, "августа": 8,
            "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
        }

        if month_name:
            month = month_map.get(month_name)
        else:
            month = reference_date.month

        year = reference_date.year
        try:
            target_date = datetime(year, month, day).date()
            if target_date < reference_date.date():
                target_date = datetime(year+1, month, day).date()
            result["date"] = target_date
            result["date_str"] = target_date.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Поиск времени будильника
    time_match = re.search(r"\b(\d{1,2})(?:[:.\s](\d{1,2}))?\s*(утра|вечера|ночи|дня)?\b", text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        period = time_match.group(3)

        # Коррекция времени по периоду дня
        if period:
            if period in ["вечера", "ночи"] and 1 <= hour <= 11:
                hour += 12
            elif period == "дня" and 1 <= hour <= 11:
                hour += 12
            elif period == "утра" and hour == 12:
                hour = 0

        # Ограничение значений времени
        hour = max(0, min(23, hour))
        minute = max(0, min(59, minute))

        result["time"] = f"{hour:02d}:{minute:02d}"

        # Определение даты для будильника
        alarm_time = datetime.strptime(result["time"], "%H:%M").time()
        current_time = reference_date.time()

        # Если время уже прошло сегодня - ставим на завтра
        if alarm_time <= current_time:
            result["date"] = reference_date + timedelta(days=1)
        else:
            result["date"] = reference_date

        result["date_str"] = result["date"].strftime("%Y-%m-%d")

    # Дефолтные значения для периода
    if not result["date"] and result["period"]:
        result["date"] = reference_date
        result["date_str"] = reference_date.strftime("%Y-%m-%d")

    return result

def extract_video_title(text, cmd_pos, app_pos):
    """Извлекаем название видео"""
    if cmd_pos[1] < app_pos[0]:
        title = text[cmd_pos[1]:app_pos[0]].strip()
    else:
        title = text[cmd_pos[1]:].strip()

    # Удаляем предлоги на границах
    title = re.sub(r"^(на|в|с|через|приложении?|включи в)\s+|\s+(на|в|с|через|приложении?)$", "", title, flags=re.IGNORECASE)
    return title.strip()

def extract_entities(text):
    """Собственно извлечение сущностей"""
    doc = nlp(text.lower())
    entities = {
        "room": None, "device": None, "value": None,
        "application": None, "video_title": None, "city": None,
        "weather": {"date": None, "period": None},
        "alarm": {"time": None, "date": None, "period": None}
    }

    # Извлечение города
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:
            entities["city"] = normalize_city(ent.text)
            break

    # Извлечение комнаты
    for token in doc:
        lemma = token.lemma_.lower()
        if lemma in ROOM_MAP:
            entities["room"] = ROOM_MAP[lemma]
            break

    # Извлечение устройства
    for token in doc:
        lemma = token.lemma_.lower()
        for dev_key, dev_list in DEVICES_MAP.items():
            if lemma in dev_list:
                entities["device"] = dev_key
                break
        if entities["device"]:
            break

    # Извлечение числового значения
    for token in doc:
        if token.like_num:
            entities["value"] = token.text
            break

    # Поиск приложений и видео
    text_lower = text.lower()
    cmd_match = None
    app_match = None

    # Поиск команды для видео
    for cmd in VIDEO_CMDS:
        match = re.search(rf"\b{re.escape(cmd)}\b", text_lower)
        if match:
            cmd_match = (match.start(), match.end())
            break

    # Поиск приложения
    app_entries = []
    for app_name, variants in APP_MAP.items():
        for variant in variants:
            app_entries.append((app_name, variant))
    app_entries.sort(key=lambda x: len(x[1]), reverse=True)

    for app_name, variant in app_entries:
        match = re.search(rf"\b{re.escape(variant)}\b", text_lower)
        if match:
            app_match = (match.start(), match.end())
            entities["application"] = app_name
            break

    # Извлечение названия видео
    if cmd_match and app_match:
        entities["video_title"] = extract_video_title(text, cmd_match, app_match)

    # Погода
    is_weather_query = any(
        re.search(rf"\b{re.escape(cmd)}\b", text.lower())
        for cmd in WEATHER_CMDS
    )

    if is_weather_query:
        time_data = parse_datetime(text)
        entities["weather"] = {
            "date": time_data["date_str"],
            "period": time_data["period"]
        }
        # Для периодов без указания даты используем сегодня
        if not time_data["date_str"] and time_data["period"]:
            entities["weather"]["date"] = datetime.now().strftime("%Y-%m-%d")

    # Обработка будильников
    is_alarm_query = any(
        re.search(rf"\b{re.escape(cmd)}\b", text.lower())
        for cmd in ALARM_CMDS
    )

    if is_alarm_query:
        time_data = parse_datetime(text)
        entities["alarm"] = {
            "time": time_data["time"],
            "date": time_data["date_str"],
            "period": time_data["period"]
        }
        # Если указан период, но не время - устанавливаем дефолтное время
        if not time_data["time"] and time_data["period"]:
            default_times = {
                "утро": "08:00",
                "день": "13:00",
                "вечер": "18:00",
                "ночь": "23:00"
            }
            entities["alarm"]["time"] = default_times.get(time_data["period"], "08:00")

    return entities

# Оценка вероятности намерения через косинусное сходство
def intent_confidence(text, intent_keywords):
    doc = nlp(text.lower())
    max_score = 0.0
    for kw in intent_keywords:
        kw_doc = nlp(kw)
        sim = doc.similarity(kw_doc)
        if sim > max_score:
            max_score = sim
    return max_score

