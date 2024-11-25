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
    
    # Extract existing fields
    tone = data.get("tone")
    brand_voice = data.get("brand_voice")
    target_audience = data.get("target_audience")
    word_count = data.get("word_count")
    main_prompt = data.get("main_prompt")
    language = data.get("language")
    content_style = data.get("content_style")
    keywords = data.get("keywords", "").strip()
    
    # Extract new fields
    create_title = data.get("create_title", False)
    create_slug = data.get("create_slug", False)
    create_meta = data.get("create_meta", False)
    
    # Extract knowledge sources and priorities
    knowledge_source_1 = data.get("knowledge_source_1", "").strip()
    knowledge_source_2 = data.get("knowledge_source_2", "").strip()
    priority_1 = int(data.get("priority_1", 5))
    priority_2 = int(data.get("priority_2", 5))
    
    # Add knowledge sources to prompt if provided
    knowledge_sources = []
    if knowledge_source_1:
        knowledge_sources.append(f"Knowledge Source 1 (Priority: {priority_1}/10):\n{knowledge_source_1}")
    if knowledge_source_2:
        knowledge_sources.append(f"Knowledge Source 2 (Priority: {priority_2}/10):\n{knowledge_source_2}")
    
    knowledge_prompt = "\n\nReference Materials:\n" + "\n\n".join(knowledge_sources) if knowledge_sources else ""
    
    prompt = f"""
    Content Generation Request:
    
    Main Prompt: {main_prompt}
    {knowledge_prompt}

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
    {additional_prompt if additional_requests else ''}

    Please generate the content based on the main prompt, considering all specified parameters.
    If additional elements were requested (title, slug, meta description), please provide them
    clearly separated before the main content using appropriate headers.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        if response and hasattr(response, 'text'):
            return jsonify({"content": response.text})
        else:
            return jsonify({"error": "Failed to generate content"}), 500

    except Exception as e:
        print(f"Error during content generation: {str(e)}")
        return jsonify({"error": f"Exception occurred: {str(e)}"}), 500

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Heroku provides the PORT environment
    app.run(host='0.0.0.0', port=port)  # Run on 0.0.0.0 to allow external access
