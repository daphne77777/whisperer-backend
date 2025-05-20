from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

message_limit = 10
session_counter = {"messages": 0, "tokens_used": 0}

@app.route("/")
def index():
    return send_from_directory('.', 'gpt-whisperer.html')

def stream_gpt_response(messages):
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        yield delta

@app.route("/chat", methods=["POST"])
def chat():
    global session_counter

    if session_counter["messages"] >= message_limit:
        return jsonify({"message": "Let’s rest for now and come back fresh tomorrow 🕊️"})

    user_message = request.json.get("message", "")

    messages = [
        {"role": "system", "content": "You are GPT Whisperer, a kind, spiritually comforting guide who responds with warmth, truth, and gentleness. Use scripture when needed."},
        {"role": "user", "content": user_message}
    ]

    def generate():
        token_count = 0
        for chunk in stream_gpt_response(messages):
            token_count += len(chunk.split())
            yield chunk
        session_counter["tokens_used"] += token_count

    session_counter["messages"] += 1
    return Response(generate(), mimetype='text/plain')

@app.route("/usage", methods=["GET"])
def usage():
    return jsonify({
        "messages": session_counter["messages"],
        "tokens_used": session_counter["tokens_used"]
    })

if __name__ == "__main__":
    app.run(debug=True)
