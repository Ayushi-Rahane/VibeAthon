import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_videos():
    data = request.get_json() or {}
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "Missing 'query' in request body."}), 400

    max_results = int(data.get('maxResults', 8))
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_results,
        'key': YOUTUBE_API_KEY
    }

    resp = requests.get(YOUTUBE_SEARCH_URL, params=params)
    if resp.status_code != 200:
        return jsonify({"error": "YouTube API error", "details": resp.json()}), resp.status_code

    items = resp.json().get('items', [])
    videos = []
    for it in items:
        vid = it.get('id', {}).get('videoId')
        snippet = it.get('snippet', {})
        videos.append({
            'id': vid,
            'title': snippet.get('title'),
            'description': snippet.get('description'),
            'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url')
                         or snippet.get('thumbnails', {}).get('default', {}).get('url')
        })

    return jsonify({"videos": videos})

if __name__ == '__main__':
    app.run(debug=True)
