from flask import Flask, request, jsonify
from textblob import TextBlob
from flask_cors import CORS
import os

app = Flask(__name__)

# ✅ CORS configuration: allow both the extension & Instagram itself
CORS(app, origins=[
    "chrome-extension://hbigpbekbbpaljaoegikneekdiejhfbk",
    "https://www.instagram.com"
])

# 🔍 Weighted keyword scoring system (English + Slovak)
KEYWORDS = {
    # 🔴 Risky (decrease trust)
    "miracle": -3, "hoax": -4, "flat earth": -5, "detox": -2, "secret": -3,
    "exposed": -2, "5g": -4, "cure": -2, "plandemic": -5, "conspiracy": -4, "fake": -3,
    "zázrak": -3, "plochá zem": -5, "tajomstvo": -3, "odhalené": -2, "liek": -2,
    "plandémia": -5, "konšpirácia": -4, "falošné": -3,

    # 🟢 Trust-boosting (increase trust)
    "source": +2, "study": +3, "peer-reviewed": +4, "research": +2,
    "data": +2, "report": +1, "zdroj": +2, "štúdia": +3,
    "vedecký článok": +4, "výskum": +2, "údaje": +2, "správa": +1
}

@app.route("/analyze", methods=["POST"])
def analyze_caption():
    data = request.get_json()
    caption = data.get("caption", "").lower()

    # --- Initial score and risk check ---
    score = 5  # neutral baseline
    risk_detected = False

    for keyword, weight in KEYWORDS.items():
        if keyword in caption:
            score += weight
            if weight < 0:
                risk_detected = True

    # --- Bonus for clean language ---
    if not risk_detected:
        score += 2

    # --- NLP with TextBlob ---
    blob = TextBlob(caption)
    polarity = blob.sentiment.polarity        # -1 to 1
    subjectivity = blob.sentiment.subjectivity  # 0 to 1

    # --- Adjust score based on NLP ---
    if subjectivity > 0.6:
        score -= 1  # too subjective
    if polarity > 0.5 or polarity < -0.5:
        score -= 1  # too emotional
    if abs(polarity) < 0.3:
        score += 2  # bonus for being neutral

    # --- Clamp and return final score ---
    score = round(max(1, min(score, 10)))

    return jsonify({
        "score": score,
        "details": {
            "keywords": "✅" if risk_detected else "🟢",
            "subjectivity": subjectivity,
            "polarity": polarity
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
