
from flask import Flask, request, jsonify, Response, send_from_directory
import openai
import os

app = Flask(__name__)

# Add your OpenAI API key here
openai.api_key = "YOUR_API_KEY_HERE"

message_limit = 10
session_counter = {"messages": 0, "tokens_used": 0}

@app.route("/")
def index():
    return send_from_directory('.', 'gpt-whisperer.html')

def stream_gpt_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5",
        messages=messages,
        stream=True
    )
    for chunk in response:
        if 'choices' in chunk and chunk['choices'][0]['delta'].get('content'):
            yield chunk['choices'][0]['delta']['content']

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
