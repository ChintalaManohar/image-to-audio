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
    # 1️⃣ Check image
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    # 2️⃣ Check API key
    if not OCR_API_KEY:
        return jsonify({"error": "OCR API key not configured"}), 500

    image_file = request.files["image"]

    # 3️⃣ Call OCR API
    try:
        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": image_file},
            data={
                "apikey": OCR_API_KEY,
                "language": "eng"
            },
            timeout=30
        )
    except Exception as e:
        return jsonify({"error": "Failed to reach OCR service"}), 500

    # 4️⃣ Parse OCR response safely
    try:
        data = response.json()
    except Exception:
        return jsonify({"error": "Invalid OCR API response"}), 500

    # 5️⃣ Handle OCR API errors
    if data.get("IsErroredOnProcessing"):
        return jsonify({
            "error": "OCR processing failed",
            "details": data.get("ErrorMessage")
        }), 400

    parsed_results = data.get("ParsedResults")
    if not parsed_results or len(parsed_results) == 0:
        return jsonify({"error": "No parsed text returned"}), 400

    extracted_text = parsed_results[0].get("ParsedText", "").strip()
    if not extracted_text:
        return jsonify({"error": "No text found in image"}), 400

    # 6️⃣ Text-to-speech
    audio_buffer = BytesIO()
    try:
        tts = gTTS(extracted_text, lang="en")
        tts.write_to_fp(audio_buffer)
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
