from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import google.generativeai as genai
from firebase import firebase_auth_required,is_enough_to_pay_modal,decrement_credit_by_amount

app = Flask(__name__)
CORS(app)

load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("API key not found. Please check your environment variables.")

# Initialize the genai library with the API key
genai.configure(api_key=API_KEY)

@app.route('/')
def index():
    return jsonify({"status": "ok"})

@app.route('/generate-content', methods=['POST'])
@firebase_auth_required
def generate_content():
    try:
        model_run_cost=15
        auth_user_id=request.auth_user_id
        auth_user_email=request.auth_email
        print('following user try to use modal',auth_user_email)
        
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Validate required fields
        required_fields = ['main_prompt', 'word_count']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # validate whether user have enough credit to run model
        is_allowed_by_cost = is_enough_to_pay_modal(auth_user_id,model_run_cost)
        if not is_allowed_by_cost:
            return jsonify({"error": "Failed to run modal due to low credit, please buy credits"}), 400


        # Extract data from request
        main_prompt = data.get('main_prompt')
        knowledge_prompt = data.get('knowledge_source', '')
        tone = data.get('tone')
        brand_voice = data.get('brand_voice')
        target_audience = data.get('target_audience')
        word_count = data.get('word_count')
        language = data.get('language')
        content_style = data.get('content_style')
        keywords = data.get('keywords')
        
        # Handle additional requests
        additional_requests_data = data.get('additional_requests', {})
        additional_requests = build_additional_requests(
            additional_requests_data.get('create_title', False),
            additional_requests_data.get('create_slug', False),
            additional_requests_data.get('create_meta', False)
        )

        prompt = f"""
        Content Generation Request:
        
        Main Prompt: {main_prompt}

        Parameters:
        - Tone: {tone if tone else 'Not specified'}
        - Brand Voice: {brand_voice if brand_voice else 'Not specified'}
        - Target Audience: {target_audience if target_audience else 'Not specified'}
        - Word Count: {word_count if word_count else 'Not specified'}
        - Language: {language if language else 'English'}
        - Content Style: {content_style if content_style else 'Not specified'}
        - Keywords: {keywords if keywords else 'Not specified'}

        Style Guidelines:
        {get_style_guidelines(content_style)}

        Additional Requests:
        {additional_requests if additional_requests else 'None'}
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        if response and hasattr(response, 'text'):
            decrement_credit_by_amount(auth_user_id,model_run_cost)
            return jsonify({"content": response.text})
        else:
            return jsonify({"error": "Failed to generate content"}), 500

    except Exception as e:
        print(f"Error during content generation: {str(e)}")
        return jsonify({
            "error": "Content generation failed",
            "details": str(e)
        }), 500

def get_style_guidelines(style):
    guidelines = {
        "formal": "Use long, well-structured paragraphs with detailed explanations. Maintain a scholarly tone while avoiding academic citations.",
        "concise": "Use short, focused paragraphs. Include bullet points for key information. Prioritize clarity and brevity.",
        "outline": "Structure the content primarily with bullet points, numbered lists, or clear hierarchical sections. Minimal narrative text.",
        "conversational": "Write in a natural, speech-like manner. Use contractions and informal language where appropriate.",
        "technical": "Include detailed technical information and specialized terminology. Focus on accuracy and precision.",
        "creative": "Use rich, descriptive language with vivid imagery. Engage the reader's imagination.",
        "minimalist": "Use the fewest words possible while maintaining clarity. Focus on essential information only."
    }
    return guidelines.get(style, "Use a balanced, professional writing style.")

def build_additional_requests(create_title, create_slug, create_meta):
    requests = []
    if create_title:
        requests.append("- Generate a compelling article title")
    if create_slug:
        requests.append("- Create a URL-friendly slug")
    if create_meta:
        requests.append("- Generate a meta description/excerpt")
    return "\n".join(requests) if requests else "None"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Heroku provides the PORT environment
    app.run(host='0.0.0.0', port=port)  # Run on 0.0.0.0 to allow external access
