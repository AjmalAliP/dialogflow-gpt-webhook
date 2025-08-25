from flask import Flask, request, jsonify
import requests
import os
import time

app = Flask(__name__)

# Hugging Face Space URL
SPACE_URL = "https://huggingface.co/spaces/CallmeStrange/dialogflow-gpt-chatbot"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True)
    user_message = req.get('queryResult', {}).get('queryText', '')

    gpt_reply = "I’m thinking… try again in a moment!"

    try:
        # Send POST request to Hugging Face Space
        response = requests.post(SPACE_URL, json={"data": [user_message]}, timeout=10)

        if response.status_code == 200 and response.content:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                gpt_reply = result[0]
            else:
                gpt_reply = f"Unexpected response format: {result}"
        else:
            gpt_reply = f"Error from Space: {response.status_code}"

    except Exception as e:
        gpt_reply = f"Exception occurred: {str(e)}"

    return jsonify({
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [gpt_reply]
                }
            }
        ]
    })

@app.route('/')
def home():
    return "Webhook server is running!"

# Use dynamic port for Render
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
