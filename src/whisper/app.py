from flask import Flask, request, jsonify
from faster_whisper import WhisperModel
import os

app = Flask(__name__)
model = WhisperModel("base", device="cpu")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    path = data.get("path")

    if not path or not os.path.exists(path):
        return jsonify({"error": "Invalid file path"}), 400

    segments, _ = model.transcribe(path)
    transcript = " ".join([seg.text for seg in segments])

    return jsonify({"transcript": transcript}), 200

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5632)
