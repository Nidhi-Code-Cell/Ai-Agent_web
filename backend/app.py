from flask import Flask, request, jsonify
from gemini import get_llm_response
from flask_cors import CORS
from dotenv import load_dotenv
import os

app=Flask(__name__)
CORS(app)


load_dotenv()  # take environment variables from .env
api_key = os.getenv("GEMINI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat_api():
    data=request.get_json()
    user_message = data.get("userQuery","")
    reply=get_llm_response(user_message)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
