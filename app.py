from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Weighted keyword trust scoring system (English + Slovak)
KEYWORDS = {
    # 🔴 RISKY TERMS (English)
    "miracle": -3,
    "hoax": -4,
    "flat earth": -5,
    "detox": -2,
    "secret": -3,
    "exposed": -2,
    "5g": -4,
    "cure": -2,
    "plandemic": -5,
    "conspiracy": -4,
    "fake": -3,

    # 🔴 RISKY TERMS (Slovak)
    "zázrak": -3,
    "hoax": -4,
    "plochá zem": -5,
    "detox": -2,
    "tajomstvo": -3,
    "odhalené": -2,
    "5g": -4,
    "liek": -2,
    "plandémia": -5,
    "konšpirácia": -4,
    "falošné": -3,

    # 🟢 TRUST TERMS (English)
    "source": +2,
    "study": +3,
    "peer-reviewed": +4,
    "research": +2,
    "data": +2,
    "report": +1,

    # 🟢 TRUST TERMS (Slovak)
    "zdroj": +2,
    "štúdia": +3,
    "vedecký článok": +4,
    "výskum": +2,
    "údaje": +2,
    "správa": +1
}

@app.route("/analyze", methods=["POST"])
def analyze_caption():
    data = request.get_json()
    caption = data.get("caption", "").lower()

    score = 5
    risk_detected = False

    for keyword, weight in KEYWORDS.items():
        if keyword in caption:
            score += weight
            if weight < 0:
                risk_detected = True

    # 🎁 Bonus if no risky keywords are found
    if not risk_detected:
        score += 2

    # Clamp the score
    score = max(1, min(score, 10))

    return jsonify({"score": score})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
