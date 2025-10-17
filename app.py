from flask import Flask, jsonify, request, session
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from openai import OpenAI
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# creating the flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-default-secret-key')  # Add this
CORS(app)

# In-memory storage for conversations
conversations = {}

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

@app.route('/v1/api/ai/respond', methods=['POST'])
def respond():
    data = request.get_json()
    user_message = data.get('message')
    user_id = data.get('userId') 
    user_assets = data.get('assets')
    user_liabilities = data.get('liabilities')

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    # Initialize conversation history for new users
    if user_id not in conversations:
        conversations[user_id] = []

    # Add user message to history
    conversations[user_id].append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })

    # Keep only last 10 messages for context
    if len(conversations[user_id]) > 10:
        conversations[user_id] = conversations[user_id][-10:]

    financial_context = ""
    if user_assets:
        financial_context += f"My assets are: {user_assets}. "
    if user_liabilities:
        financial_context += f"My liabilities are: {user_liabilities}. "

    combined_user_message = f"{financial_context}{user_message}"

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Create messages array with conversation history
        messages = [
            {
                "role": "system",
                "content": "Your name is Finley, an AI-powered personal finance assistant. "
                "You help users manage their finances, offering advice on budgeting, saving, investing, "
                "and financial planning. Base your guidance on user input, past conversations, and any "
                "manually provided net worth information. "
                "Always respond in a friendly, approachable, and clear manner. "
                "All information you provide is for educational purposes only. "
                "You cannot edit or delete any user data. "
                "If you don't know the answer to a question, respond with: "
                "'I'm sorry, I don't have that information.'"
            }
        ]

        # Add conversation history
        for msg in conversations[user_id]:
            messages.append({
                "role": "user" if msg["role"] == "user" else "assistant",
                "content": msg["content"]
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": combined_user_message
        })

        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2-Exp:novita",
            messages=messages,
        )

        ai_reply = completion.choices[0].message.content

        # Store AI response in conversation history
        conversations[user_id].append({
            "role": "assistant",
            "content": ai_reply,
            "timestamp": datetime.now().isoformat()
        })

        return jsonify({
            "response": ai_reply,
            "conversation_history": conversations[user_id]
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Server error"}), 500
    
# running the app
if __name__ == '__main__':
    app.run(debug=True)