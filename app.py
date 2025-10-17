# using flask_restful
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# creating the flask app
app = Flask(__name__)
# Allow CORS for all domains on all routes (for development purposes)
CORS(app)

HF_API_URL = "https://api-inference.huggingface.co/models/distilgpt2"
HEADERS = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

@app.route('/v1/api/ai/respond', methods=['POST'])
def respond():
    data = request.get_json()
    message = data.get('message')

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        response = requests.post(
            HF_API_URL,
            headers=HEADERS,
            json={"inputs": message},
            timeout=30
        )

        if response.status_code != 200:
            print("Hugging Face Error:", response.text)
            return jsonify({"error": "Failed to fetch AI response"}), response.status_code

        result = response.json()

        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
            ai_reply = result[0]["generated_text"]
        else:
            ai_reply = str(result)

        return jsonify({"response": ai_reply})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)