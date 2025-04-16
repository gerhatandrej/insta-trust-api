from flask import Flask, request, jsonify
from textblob import TextBlob
from flask_cors import CORS
import os

app = Flask(__name__)
from flask_cors import CORS

CORS(app, origins=["chrome-extension://hbigpbekbbpaljaoegikneekdiejhfbk"])


# Weighted keyword scoring system (English + Slovak)
KEYWORDS = {
    # 🔴 Risky (decrease trust)
    "miracle": -3, "hoax": -4, "flat earth": -5, "detox": -2, "secret": -3,
    "exposed": -2, "5g": -4, "cure": -2, "plandemic": -5, "conspiracy": -4, "fake": -3,
    "zázrak": -3, "hoax": -4, "plochá zem": -5, "detox": -2, "tajomstvo": -3,
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
    score = 5  # neutral start
    risk_detected = False

    for keyword, weight in KEYWORDS.items():
        if keyword in caption:
            score += weight
            if weight < 0:
                risk_detected = True

    # --- Clean language bonus ---
    if not risk_detected:
        score += 2

    # --- NLP with TextBlob ---
    blob = TextBlob(caption)
    polarity = blob.sentiment.polarity        # -1 to 1
    subjectivity = blob.sentiment.subjectivity  # 0 to 1

    # NLP scoring adjustments
    if subjectivity > 0.6:
        score -= 1  # too subjective
    if polarity > 0.5 or polarity < -0.5:
        score -= 1  # very emotional (positive or negative)

    # Clamp final score between 1 and 10
    score = round(max(1, min(score, 10)))

