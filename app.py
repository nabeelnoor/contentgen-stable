from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, auth



app = Flask(__name__)
CORS(app)

load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("API key not found. Please check your environment variables.")

# Initialize the genai library with the API key
genai.configure(api_key=API_KEY)

# initialize firebase sdk credentials
firebase_credentials = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),  # Handle multiline keys
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain":os.getenv('FIREBASE_UNIVERSE_DOMAIN')
}

print("\ndebug-start\n",firebase_credentials,"\ndebug-end\n")
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)

def firebase_auth_required(func):
    def wrapper(*args, **kwargs):
        id_token = request.headers.get('Authorization')  # Expecting "Bearer <token>"
        if not id_token or not id_token.startswith("Bearer "):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401
        id_token = id_token.split("Bearer ")[1]

        user_id = verify_id_token(id_token)
        
        print("\ndebug-start\n",user_id,"\ndebug-end\n")

        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Optionally, attach user_id to request context
        request.user_id = user_id
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-content', methods=['POST'])
def generate_content():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Validate required fields
        required_fields = ['main_prompt', 'word_count']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400

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
