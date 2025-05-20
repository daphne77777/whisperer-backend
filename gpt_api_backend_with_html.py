import os
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)  # allow your Mobirise‐hosted page to talk to this API

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_msg = data.get("message", "")
    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    def stream():
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content": user_msg}],
            stream=True
        )
        for chunk in resp:
            delta = chunk.choices[0].delta.get("content")
            if delta:
                yield delta

    return Response(stream(), content_type="text/plain")

@app.route("/usage", methods=["GET"])
def usage():
    # you can plug in real counters here if you log usage in Redis/etc.
    return jsonify({"messages": 0, "tokens_used": 0})

# (optional) serve your HTML from here if you want a 1-repo deploy:
@app.route("/", methods=["GET"])
def index():
    return app.send_static_file("gpt-whisperer.html")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # *** bind to 0.0.0.0 so Render can see your web port ***
    app.run(host="0.0.0.0", port=port)
