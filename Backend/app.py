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

    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": image_file},
        data={
            "apikey": OCR_API_KEY,
            "language": "eng",
            "OCREngine": 2
        }
    )

    data = response.json()
    print("OCR RESPONSE:", data)   # 🔴 VERY IMPORTANT

    if data.get("IsErroredOnProcessing"):
        error_text = "Sorry, I could not read text from the image."
        audio = BytesIO()
        gTTS(error_text, lang="en").write_to_fp(audio)
        audio.seek(0)
        return send_file(audio, mimetype="audio/mpeg"), 200


    results = data.get("ParsedResults")
    if not results:
        return jsonify({"error": "No OCR results"}), 400

    text = results[0].get("ParsedText", "").strip()
    if not text:
        return jsonify({"error": "No text detected"}), 400

    audio = BytesIO()
    gTTS(text, lang="en").write_to_fp(audio)
    audio.seek(0)

    return send_file(audio, mimetype="audio/mpeg"), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
