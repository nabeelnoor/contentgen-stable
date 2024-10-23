from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import google.generativeai as genai

app = Flask(__name__)

load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("API key not found. Please check your environment variables.")

# Initialize the genai library with the API key
genai.configure(api_key=API_KEY)

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

    # Prepare the input prompt with optional parameters (tone, brand_voice, etc.)
    prompt = main_prompt
    if tone:
        prompt += f"\nTone: {tone}"
    if brand_voice:
        prompt += f"\nBrand voice: {brand_voice}"
    if word_count:
        prompt += f"\nWord count: {word_count}"

    try:
        # Use the gemini model to generate content
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Handle the response from the Gemini API
        if response and 'text' in response:
            return jsonify({"content": response.text})
        else:
            return jsonify({"error": "Failed to generate content"}), 500

    except Exception as e:
        print(f"Error during content generation: {str(e)}")
        return jsonify({"error": f"Exception occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Heroku provides the PORT environment
    app.run(host='0.0.0.0', port=port)  # Run on 0.0.0.0 to allow external access
