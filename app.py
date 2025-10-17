# using flask_restful
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# creating the flask app
app = Flask(__name__)
# Allow CORS for all domains on all routes (for development purposes)
CORS(app)

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

@app.route('/v1/api/ai/respond', methods=['POST'])
def respond():
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2-Exp:novita",
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ],
        )

        ai_reply = completion.choices[0].message.content

        return jsonify({"response": ai_reply})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)