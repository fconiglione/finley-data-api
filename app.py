# using flask_restful
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import requests

# creating the flask app
app = Flask(__name__)

@app.route('/v1/api/ai/respond', methods=['POST'])
def respond():
    data = request.get_json()
    user_message = data.get('message')

    ai_response = f"AI Response to: {user_message}"

    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(debug=True)