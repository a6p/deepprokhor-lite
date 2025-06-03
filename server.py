from flask import Flask, request, jsonify
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from entity_extractor import extract_entities, intent_confidence

app = Flask(__name__)

#"DeepPavlov/rubert-base-cased"

#cointegrated/rubert-tiny (10x быстрее, 10x меньше)

#cointegrated/rubert-tiny2 — самая лёгкая BERT-модель на русском

MODEL_NAME = "./finetuned_model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()

INTENTS = [
  "turn_on_light",        # 0
  "turn_off_light",       # 1
  "set_temperature",      # 2
  "turn_on_conditioner",  # 3
  "turn_off_conditioner", # 4
  "play_music",           # 5
  "stop_music",           # 6
  "weather_query",        # 7
  "set_alarm",            # 8
  "turn_on_tv",           # 9
  "turn_off_tv",          #10
  "tv_channel_switch",    #11
  "tv_android"            #12
]

def predict_intent(text: str):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=1).cpu().numpy()[0]
    max_idx = probs.argmax()
    return INTENTS[max_idx], float(probs[max_idx])

@app.route("/nlp", methods=["POST"])
def nlp_handler():
    data = request.get_json(force=True)
    text = data.get("text", "").lower()
    if not text:
        return jsonify({"error": "Empty text"}), 400

    intent, confidence = predict_intent(text)
    entities = extract_entities(text)  # функция для извлечения сущностей

    CONFIDENCE_THRESHOLD = 0.6
    if confidence < CONFIDENCE_THRESHOLD:
        intent = "unknown_command"

    return jsonify({
        "text": text,
        "intent": intent,
        "intent_score": round(confidence, 3),
        "entities": entities
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

