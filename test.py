import unittest
import requests
from datetime import datetime, timedelta

class TestNLPAPI(unittest.TestCase):
    BASE_URL = "http://localhost:8080/nlp"
    HEADERS = {"Content-Type": "application/json"}
   
    # Динамически вычисляем даты
    today = datetime.now()
    tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
                    
    # Вычисляем дату следующей субботы
    current_weekday = today.weekday()
    days_to_saturday = (5 - current_weekday) % 7 or 7
    next_saturday = (today + timedelta(days=days_to_saturday)).strftime("%Y-%m-%d")
    
    def test_weather_queries(self):
        test_cases = [
            {
                "text": "будет дождь завтра",
                "expected": {
                    "intent": "weather_query",
                    "entities": {
                        "weather": {"date": self.tomorrow, "period": None},
                        "city": None
                    }
                }
            },
            {
                "text": "будет дождь завтра утром",
                "expected": {
                    "intent": "weather_query",
                    "entities": {
                        "weather": {"date": self.tomorrow, "period": "утро"},
                        "city": None
                    }
                }
            },
            {
                "text": "будет дождь завтра утром в москве",
                "expected": {
                    "intent": "weather_query",
                    "entities": {
                        "weather": {"date": self.tomorrow, "period": "утро"},
                        "city": "москва"
                    }
                }
            },
            {
                "text": "какая погода в субботу",
                "expected": {
                    "intent": "weather_query",
                    "entities": {
                        "weather": {"date": self.next_saturday, "period": None},
                        "city": None
                    }
                }
            },
            {
                "text": "какая погода в на выходных",
                "expected": {
                    "intent": "weather_query",
                    "entities": {
                        "weather": {"date": self.next_saturday, "period": "weekend"},
                        "city": None
                    }
                }
            }
        ]

        for case in test_cases:
            with self.subTest(case=case["text"]):
                response = requests.post(
                    self.BASE_URL,
                    headers=self.HEADERS,
                    json={"text": case["text"]}
                )
                data = response.json()

                self.assertEqual(data["intent"], case["expected"]["intent"])
                self.assertDictEqual(data["entities"]["weather"], case["expected"]["entities"]["weather"])

                if case["expected"]["entities"]["city"]:
                    self.assertEqual(data["entities"]["city"], case["expected"]["entities"]["city"])
                else:
                    self.assertIsNone(data["entities"]["city"])
    
    def test_alarm_queries(self):
        test_cases = [
            {
                "text": "будильник на 7 вечера",
                "expected": {
                    "intent": "set_alarm",
                    "entities": {
                        "alarm": {"time": "19:00", "date": self.today.strftime("%Y-%m-%d"), "period": "вечер"}
                    }
                }
            },
            {
                "text": "будильник на 7 утра",
                "expected": {
                    "intent": "set_alarm",
                    "entities": {
                        "alarm": {"time": "07:00", "date": self.tomorrow, "period": None}
                    }
                }
            },
            {
                "text": "заведи будильник на завтра на 12 часов",
                "expected": {
                    "intent": "set_alarm",
                    "entities": {
                        "alarm": {"time": "12:00", "date": self.tomorrow, "period": None}
                    }
                }
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["text"]):
                response = requests.post(
                    self.BASE_URL,
                    headers=self.HEADERS,
                    json={"text": case["text"]}
                )
                data = response.json()
                
                self.assertEqual(data["intent"], case["expected"]["intent"])
                self.assertDictEqual(data["entities"]["alarm"], case["expected"]["entities"]["alarm"])
    
    def test_device_control_queries(self):
        test_cases = [
            {
                "text": "включи свет на кухне",
                "expected": {
                    "intent": "turn_on_light",
                    "entities": {
                        "device": "свет",
                        "room": "кухня",
                        "value": None
                    }
                }
            },
            {
                "text": "включи кондиционер на 22 градуса",
                "expected": {
                    "intent": "set_temperature",
                    "entities": {
                        "device": "кондиционер",
                        "room": None,
                        "value": "22"
                    }
                }
            },
            {
                "text": "выключи телевизор в спальне",
                "expected": {
                    "intent": "turn_off_tv",
                    "entities": {
                        "device": "телевизор",
                        "room": "спальня",
                        "value": None
                    }
                }
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["text"]):
                response = requests.post(
                    self.BASE_URL,
                    headers=self.HEADERS,
                    json={"text": case["text"]}
                )
                data = response.json()
                
                self.assertEqual(data["intent"], case["expected"]["intent"])
                self.assertEqual(data["entities"]["device"], case["expected"]["entities"]["device"])
                self.assertEqual(data["entities"]["room"], case["expected"]["entities"]["room"])
                self.assertEqual(data["entities"]["value"], case["expected"]["entities"]["value"])
    
    def test_media_queries(self):
        test_cases = [
            {
                "text": "включи маша и медведь на ютуб",
                "expected": {
                    "intent": "tv_android",
                    "entities": {
                        "application": "youtube",
                        "video_title": "маша и медведь"
                    }
                }
            },
            {
                "text": "покажи смешарики в ютуб музик",
                "expected": {
                    "intent": "tv_android",
                    "entities": {
                        "application": "youtube music",
                        "video_title": "смешарики"
                    }
                }
            },
            {
                "text": "включи телевизор на 1 канал",
                "expected": {
                    "intent": "tv_channel_switch",
                    "entities": {
                        "device": "телевизор",
                        "value": "1"
                    }
                }
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["text"]):
                response = requests.post(
                    self.BASE_URL,
                    headers=self.HEADERS,
                    json={"text": case["text"]}
                )
                data = response.json()
                
                self.assertEqual(data["intent"], case["expected"]["intent"])
                
                if "application" in case["expected"]["entities"]:
                    self.assertEqual(data["entities"]["application"], case["expected"]["entities"]["application"])
                
                if "video_title" in case["expected"]["entities"]:
                    self.assertEqual(data["entities"]["video_title"], case["expected"]["entities"]["video_title"])
                
                if "device" in case["expected"]["entities"]:
                    self.assertEqual(data["entities"]["device"], case["expected"]["entities"]["device"])
                
                if "value" in case["expected"]["entities"]:
                    self.assertEqual(data["entities"]["value"], case["expected"]["entities"]["value"])
    
    def test_invalid_queries(self):
        test_cases = [
            {
                "text": "купи слона",
                "expected": {
                    "intent": "unknown_command",
                    "entities": {}
                }
            },
            {
                "text": "возьми с полки пирожок",
                "expected": {
                    "intent": "unknown_command",
                    "entities": {}
                }
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["text"]):
                response = requests.post(
                    self.BASE_URL,
                    headers=self.HEADERS,
                    json={"text": case["text"]}
                )
                data = response.json()
                
                self.assertEqual(data["intent"], case["expected"]["intent"])
                self.assertFalse(data["entities"])  # Не должно быть извлеченных сущностей

if __name__ == "__main__":
    unittest.main()
