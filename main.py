
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Hugging Face API setup
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True)
    user_message = req.get('queryResult', {}).get('queryText', '')

    # Send message to Hugging Face model
    response = requests.post(API_URL, headers=headers, json={"inputs": user_message})
    result = response.json()

    # Extract response text
    try:
        if isinstance(result, list) and 'generated_text' in result[0]:
            gpt_reply = result[0]['generated_text']
        elif isinstance(result, dict) and 'generated_text' in result:
            gpt_reply = result['generated_text']
        else:
            gpt_reply = f"Unexpected response format: {result}"
    except Exception as e:
        gpt_reply = f"Error processing response: {str(e)}"


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

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
