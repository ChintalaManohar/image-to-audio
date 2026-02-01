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

    image_file = request.files["image"]

    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": image_file},
        data={
            "apikey": OCR_API_KEY,
            "language": "eng"
        }
    )

    data = response.json()

    try:
        extracted_text = data["ParsedResults"][0]["ParsedText"].strip()
    except:
        return jsonify({"error": "OCR failed"}), 500

    if not extracted_text:
        return jsonify({"error": "No text found"}), 400

    audio_buffer = BytesIO()
    tts = gTTS(extracted_text, lang="en")
    tts.write_to_fp(audio_buffer)
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
