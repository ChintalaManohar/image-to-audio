from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from gtts import gTTS
from io import BytesIO
import requests
import os

app = Flask(__name__)
CORS(app)

OCR_API_KEY = os.environ.get("OCR_API_KEY")

@app.route("/convert", methods=["POST"])
def convert_image_to_audio():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    if not OCR_API_KEY:
        return jsonify({"error": "OCR API key missing"}), 500

    image_file = request.files["image"]

    try:
        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": image_file},
            data={
                "apikey": OCR_API_KEY,
                "language": "eng",
                "isOverlayRequired": False,
                "OCREngine": 2
            },
            timeout=30
        )
    except Exception as e:
        return jsonify({"error": "Failed to connect to OCR API"}), 500

    try:
        data = response.json()
    except Exception:
        return jsonify({"error": "OCR API returned invalid JSON"}), 500

    # 🔍 LOGICAL ERROR HANDLING
    if data.get("IsErroredOnProcessing"):
        return jsonify({
            "error": "OCR API error",
            "details": data.get("ErrorMessage")
        }), 400

    parsed = data.get("ParsedResults")
    if not parsed:
        return jsonify({"error": "No OCR results returned"}), 400

    text = parsed[0].get("ParsedText", "").strip()
    if not text:
        return jsonify({"error": "No text detected in image"}), 400

    audio_buffer = BytesIO()
    try:
        gTTS(text, lang="en").write_to_fp(audio_buffer)
    except Exception:
        return jsonify({"error": "Text-to-speech failed"}), 500

    audio_buffer.seek(0)

    return send_file(
        audio_buffer,
        mimetype="audio/mpeg",
        as_attachment=False,
        download_name="audio.mp3"
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
