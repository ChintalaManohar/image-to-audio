from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image
from gtts import gTTS
from io import BytesIO
import easyocr
import os

app = Flask(__name__)
CORS(app)

# Initialize OCR reader once
reader = easyocr.Reader(['en'], gpu=False)

@app.route("/convert", methods=["POST"])
def convert_image_to_audio():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = Image.open(request.files["image"]).convert("RGB")

    # OCR
    results = reader.readtext(image)
    cleaned_text = " ".join([res[1] for res in results])

    if not cleaned_text.strip():
        return jsonify({"error": "No text found in image"}), 400

    # Text to Speech
    audio_buffer = BytesIO()
    tts = gTTS(cleaned_text, lang="en")
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
