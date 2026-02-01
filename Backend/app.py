from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
from gtts import gTTS
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
CORS(app)

@app.route("/convert", methods=["POST"])
def convert_image_to_audio():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = Image.open(request.files["image"])

    text = pytesseract.image_to_string(image, config="--psm 6")
    cleaned_text = " ".join(text.split())

    if not cleaned_text:
        return jsonify({"error": "No text found"}), 400

    # 🎧 Generate audio in memory
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
    app.run(port=5000, debug=True)
