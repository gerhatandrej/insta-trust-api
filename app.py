from flask import Flask, request, jsonify
from textblob import TextBlob
from flask_cors import CORS
import os

app = Flask(__name__)

# allow only your extension _and_ instagram.com to hit the API
CORS(
    app,
    origins=[
        "chrome-extension://hbigpbekbbpaljaoegikneekdiejhfbk",
        "https://www.instagram.com"
    ]
)

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

@app.route("/analyze", methods=["POST"])
def analyze_caption():
    data = request.get_json()
    caption = data.get("caption", "").lower()

    # --- Keyword scoring ---
    score = 5
    risk_detected = False
    for kw, w in KEYWORDS.items():
        if kw in caption:
            score += w
            if w < 0:
                risk_detected = True

    # --- Clean language bonus ---
    if not risk_detected:
        score += 2

    # --- NLP with TextBlob ---
    blob = TextBlob(caption)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    # NLP adjustments
    if subjectivity > 0.6:
        score -= 1
    if polarity > 0.5 or polarity < -0.5:
        score -= 1

    # Clamp and round
    score = round(max(1, min(score, 10)))

    return jsonify({
        "score": score,
        "details": {
            "keywords": "✅" if not risk_detected else "⚠️",
            "subjectivity": subjectivity,
            "polarity": polarity
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
