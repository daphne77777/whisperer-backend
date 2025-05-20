import os
import openai
from flask import Flask, request, Response, jsonify, send_from_directory
from flask_cors import CORS

# === CONFIG ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # repo root
HTML_NAME = 'gpt-whisperer.html'

# === APP SETUP ===
app = Flask(__name__)
CORS(app)
openai.api_key = os.getenv("OPENAI_API_KEY")

# === CHAT STREAM ===
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_msg = data.get("message", "")
    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    def streamer():
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_msg}],
            stream=True
        )
        for chunk in resp:
            text = chunk.choices[0].delta.get("content")
            if text:
                yield text

    return Response(streamer(), content_type="text/plain")

# === USAGE COUNTER ===
@app.route('/usage', methods=['GET'])
def usage():
    return jsonify({"messages": 0, "tokens_used": 0})

# === SERVE YOUR HTML ===
@app.route('/', methods=['GET', 'HEAD'])
def index():
    html_path = os.path.join(BASE_DIR, HTML_NAME)
    app.logger.info(f"Index hit: looking for {html_path} — exists={os.path.exists(html_path)}")
    if not os.path.exists(html_path):
        return f"⚠️ Could not find {HTML_NAME} in {BASE_DIR}", 500
    return send_from_directory(BASE_DIR, HTML_NAME)

# === RUN ===
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    # bind to 0.0.0.0 so Render can health-check it
    app.run(host='0.0.0.0', port=port)
