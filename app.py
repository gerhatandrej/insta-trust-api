from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Simple keyword-based trust scoring
SUSPICIOUS_KEYWORDS = [
    "miracle", "hoax", "flat earth", "detox", "secret", "exposed",
    "5G", "cure", "hidden truth", "conspiracy", "fake", "plandemic"
]

@app.route("/analyze", methods=["POST"])
def analyze_caption():
    data = request.get_json()
    caption = data.get("caption", "").lower()
    
    score = 10
    for word in SUSPICIOUS_KEYWORDS:
        if word in caption:
            score -= 2

    score = max(1, score)  # Minimum score = 1
    return jsonify({"score": score})

# Make it Render-compatible
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
