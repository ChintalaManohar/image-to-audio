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
        error_text = "OCR service is not configured."
        audio = BytesIO()
        gTTS(error_text, lang="en").write_to_fp(audio)
        audio.seek(0)
        return send_file(audio, mimetype="audio/mpeg"), 200

    image_file = request.files["image"]

    # 1️⃣ Call OCR API safely
    try:
        response = requests.post(
    "https://api.ocr.space/parse/image",
    files={
        "file": (
            image_file.filename,
            image_file.stream,
            image_file.mimetype
        )
    },
    data={
        "apikey": OCR_API_KEY,
        "language": "eng",
        "OCREngine": 2,
        "scale": True
    },
    timeout=30
)

    except Exception:
        error_text = "Unable to reach OCR service."
        audio = BytesIO()
        gTTS(error_text, lang="en").write_to_fp(audio)
        audio.seek(0)
        return send_file(audio, mimetype="audio/mpeg"), 200

    # 2️⃣ Parse JSON safely
    try:
        data = response.json()
    except Exception:
        error_text = "OCR service returned an invalid response."
        audio = BytesIO()
        gTTS(error_text, lang="en").write_to_fp(audio)
        audio.seek(0)
        return send_file(audio, mimetype="audio/mpeg"), 200

    print("OCR RESPONSE:", data,flush=True)

    # 3️⃣ Handle OCR processing errors
    if data.get("IsErroredOnProcessing"):
        error_text = "Sorry, I could not read text from the image."
        audio = BytesIO()
        gTTS(error_text, lang="en").write_to_fp(audio)
        audio.seek(0)
        return send_file(audio, mimetype="audio/mpeg"), 200

    results = data.get("ParsedResults")
    if not results:
        error_text = "No readable text was found in the image."
        audio = BytesIO()
        gTTS(error_text, lang="en").write_to_fp(audio)
        audio.seek(0)
        return send_file(audio, mimetype="audio/mpeg"), 200

    text = results[0].get("ParsedText", "").strip()
    if not text:
        error_text = "The image does not contain readable text."
        audio = BytesIO()
        gTTS(error_text, lang="en").write_to_fp(audio)
        audio.seek(0)
        return send_file(audio, mimetype="audio/mpeg"), 200

    # 4️⃣ Normal success path
    audio = BytesIO()
    gTTS(text, lang="en").write_to_fp(audio)
    audio.seek(0)
    return send_file(audio, mimetype="audio/mpeg"), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
