import os
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
import wikipedia
import requests
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

app = Flask(__name__)
load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_API_URL = "https://api.pexels.com/v1/search"

@app.route("/", methods=["GET"])
def hello():
    return jsonify({"message": "Travel Guide POC working!"})

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    location = data.get("location", "Paris")

    try:
        # Get tourist attraction summary
        search_results = wikipedia.search(location)
        if not search_results:
            return jsonify({"error": "No results found"}), 404
        page = wikipedia.page(search_results[0])
        summary = wikipedia.summary(page.title, sentences=5)

        # Fetch image from Pexels
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": location, "per_page": 1}
        res = requests.get(PEXELS_API_URL, headers=headers, params=params)
        photo_url = res.json()["photos"][0]["src"]["medium"]
        img_data = requests.get(photo_url).content
        img_path = "api/image.jpg"
        with open(img_path, "wb") as f:
            f.write(img_data)

        # Use placeholder audio (silence)
        audio_path = "api/sample.mp3"
        with open(audio_path, "wb") as f:
            f.write(requests.get("https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav").content)

        # Generate MP4 using MoviePy
        clip = ImageClip(img_path).set_duration(10).resize(width=720)
        clip = clip.set_audio(AudioFileClip(audio_path))
        clip.write_videofile("static/output.mp4", fps=24)

        return send_file("static/output.mp4", as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
