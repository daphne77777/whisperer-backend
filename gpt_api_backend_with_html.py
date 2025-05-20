# Updated GPT Whisperer backend with OpenAI >=1.0.0 support

from flask import Flask, request, jsonify, stream_with_context, Response
from flask_cors import CORS
import os
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory usage tracker
usage = {"messages": 0, "tokens_used": 0}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    def generate():
        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_input}],
                stream=True
            )

            full_response = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_response += delta
                yield delta

            usage["messages"] += 1
            usage["tokens_used"] += len(full_response.split())  # Estimate tokens

        except Exception as e:
            yield f"[ERROR]: {str(e)}"

    return Response(stream_with_context(generate()), content_type='text/plain')

@app.route("/usage")
def get_usage():
    return jsonify(usage)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
