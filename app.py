from flask import Flask, request, jsonify
from textblob import TextBlob
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app, origins=["chrome-extension://hbigpbekbbpaljaoegikneekdiejhfbk"])

# Get Hugging Face API key securely from environment variable
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Weighted keyword scoring system (English + Slovak)
KEYWORDS = {
    # 🔴 Risky (decrease trust)
    "miracle": -3, "hoax": -4, "flat earth": -5, "detox": -2, "secret": -3,
    "exposed": -2, "5g": -4, "cure": -2, "plandemic": -5, "conspiracy": -4, "fake": -3,
    "zázrak": -3, "plochá zem": -5, "tajomstvo": -3,
    "odhalené": -2, "liek": -2, "plandémia": -5, "konšpirácia": -4, "falošné": -3,

    # 🟢 Trust-boosting (increase trust)
    "source": +2, "study": +3, "peer-reviewed": +4, "research": +2, "data": +2, "report": +1,
    "zdroj": +2, "štúdia": +3, "vedecký článok": +4, "výskum": +2, "údaje": +2, "správa": +1
}

def analyze_keywords(caption):
    score = 5
    risk_detected = False

    for keyword, weight in KEYWORDS.items():
        if keyword in caption:
            score += weight
            if weight < 0:
                risk_detected = True

    if not risk_detected:
        score += 2

    return score, risk_detected

def analyze_sentiment(caption):
    blob = TextBlob(caption)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    adjust = 0
    if subjectivity > 0.6:
        adjust -= 1
    if abs(polarity) > 0.5:
        adjust -= 1
    if abs(polarity) < 0.3:
        adjust += 2

    return polarity, subjectivity, adjust

def ml_trust_score(caption):
    url = "https://api-inference.huggingface.co/models/microsoft/xtremedistil-l6-h384-uncased"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": caption}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            # Just return a confidence score, normalized from 0–1 → scaled to 0–2
            confidence = result[0][0]["score"]
            return round(confidence * 2, 1)
    except Exception as e:
        print("ML API Error:", e)

    return 0  # fallback

@app.route("/analyze", methods=["POST"])
def analyze_caption():
    data = request.get_json()
    caption = data.get("caption", "").lower()

    score, risky = analyze_keywords(caption)
    polarity, subjectivity, sentiment_adjust = analyze_sentiment(caption)
    score += sentiment_adjust

    score += ml_trust_score(caption)

    score = round(max(1, min(score, 10)))

    return jsonify({
        "score": score,
        "details": {
            "keywords": "✅" if risky else "🟢",
            "polarity": polarity,
            "subjectivity": subjectivity
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
