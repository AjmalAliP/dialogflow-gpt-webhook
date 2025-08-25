from flask import Flask, request, jsonify
import requests
import os
import time

app = Flask(__name__)

# Hugging Face API setup
API_URL = "https://api-inference.huggingface.co/models/OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5"
headers = {
    "Authorization": f"Bearer {os.getenv('HF_API_KEY')}"
}

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True)
    user_message = req.get('queryResult', {}).get('queryText', '')

    # Retry logic
    max_retries = 2
    gpt_reply = "I’m thinking… try again in a moment!"
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": user_message}, timeout=10)
            result = response.json()

            # Handle different response formats
            if isinstance(result, list) and 'generated_text' in result[0]:
                gpt_reply = result[0]['generated_text']
                break
            elif isinstance(result, dict) and 'generated_text' in result:
                gpt_reply = result['generated_text']
                break
            elif 'error' in result:
                gpt_reply = f"Error from model: {result['error']}"
                break
        except Exception as e:
            gpt_reply = f"Exception occurred: {str(e)}"
            time.sleep(1)  # brief pause before retry
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
