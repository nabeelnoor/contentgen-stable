from flask import Flask, request, jsonify, render_template
import requests

from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("API key not found. Please check your environment variables.")
GEMINI_API_URL = "https://gemini-api-endpoint.com/generate-content"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-content', methods=['POST'])
def generate_content():
    data = request.json
    tone = data.get("tone")
    brand_voice = data.get("brand_voice")
    word_count = data.get("word_count")
    main_prompt = data.get("main_prompt")
    
    # Prepare the request payload for the Gemini API
    api_payload = {
        "tone": tone,
        "brand_voice": brand_voice,
        "word_count": word_count,
        "main_prompt": main_prompt
    }
    
    # Send request to Gemini API
    response = requests.post(
        GEMINI_API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=api_payload
    )

    # Handle Gemini API response
    if response.status_code == 200:
        generated_content = response.json().get('generated_content')
        return jsonify({"content": generated_content})
    else:
        return jsonify({"error": "Failed to generate content"}), 500

if __name__ == '__main__':
    app.run(debug=False)
    port = int(os.environ.get('PORT', 5000))  # Heroku provides the PORT environment
    app.run(host='0.0.0.0', port=port)  # Run on 0.0.0.0 to allow external access

