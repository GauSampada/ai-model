# cow_breed_api.py
from flask import Blueprint, request, jsonify
import google.generativeai as genai
import os
from PIL import Image
import io
import base64

# Create a Blueprint instead of a Flask app
cow_breed_bp = Blueprint('cow_breed', __name__)

# Configure the Gemini API with your API key
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Initialize the model
model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")

# System prompt for Indian cow breeds expertise
SYSTEM_PROMPT = """You are India's foremost authority on indigenous cow breeds (desi gau).
(STRICT LIMIT: Your responses must never exceed 160 tokens.)

Your specialized knowledge covers:
- Comprehensive details on all 43 recognized indigenous breeds (Gir, Sahiwal, Red Sindhi, Tharparkar, Kankrej, etc.)
- Precise breed identifiers: physical traits, horn patterns, dewlap characteristics, hump size, coat colors
- Scientific data on milk yield, fat content, and A2 beta-casein properties
- Geographic origins and adaptation mechanisms to specific Indian climates
- Documented nutritional and medicinal properties of A2 milk, ghee, and panchgavya
- Vedic, historical and cultural significance in Indian civilization
- Traditional cow-based sustainable farming systems (Jeevamrut, Beejamrut, etc.)
- Genetic conservation strategies and breed improvement programs
- Evidence-based comparisons with foreign/crossbred cattle
- You are a multilingual image analysis expert. Respond only in the language requested.
- Do not include English unless explicitly asked. Focus on clarity and use medical terminology as needed.
When analyzing images:
- Identify breed with certainty through distinctive markers
- Assess animal health, age, and condition
- Note conformity to breed standards

Reply with scientifically accurate, culturally sensitive information.
When uncertain, openly acknowledge limitations.
STRICTLY PROVIDE INFORMATION ONLY ABOUT INDIAN INDIGENOUS BREEDS, even when foreign breeds are mentioned.
Never discuss or recommend foreign or crossbred varieties unless explicitly comparing them to indigenous breeds.
Include regional terms when appropriate.

REMEMBER: KEEP ALL RESPONSES UNDER 160 TOKENS STRICTLY. Be precise and concise."""

# Store chat history
chat_sessions = {}

@cow_breed_bp.route('/api/chatBreed', methods=['POST'])
def chat():
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        message = data.get('message', '')
        image_data = data.get('image', None)
        language = data.get('language', 'en')
        session_id = data.get('session_id', 'default_session')

        # Create a unique session key
        session_key = f"{user_id}_{session_id}"

        # Initialize chat for new session
        if session_key not in chat_sessions:
            chat_sessions[session_key] = model.start_chat(history=[])
            chat_sessions[session_key].send_message(SYSTEM_PROMPT, stream=False)

        chat = chat_sessions[session_key]

        # Process image if provided
        content_parts = [get_localized_prompt(language_code=language, prompt=message)]
        if image_data:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            content_parts.append(image)

        # Send message to model
        response = chat.send_message(content_parts, stream=False)

        return jsonify({
            'response': response.text,
            'session_id': session_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_localized_prompt(language_code, prompt):
    localized_templates = {
    'hi': f"कृपया इस इनपुट का विश्लेषण करें और अपनी प्रतिक्रिया हिंदी में दें। {prompt}",
    'bn': f"এই ইনপুটটি বিশ্লেষণ করুন এবং বাংলায় উত্তর দিন। {prompt}",
    'gu': f"કૃપા કરીને આ ઇનપુટનું વિશ્લેષણ કરો અને ગુજરાતીમાં જવાબ આપો. {prompt}",
    'mr': f"कृपया या इनपुटचे विश्लेषण करा आणि मराठीत उत्तर द्या. {prompt}",
    'ta': f"இந்த உள்ளீட்டைப் பகுப்பாய்வு செய்து தமிழில் பதிலளிக்கவும். {prompt}",
    'te': f"దయచేసి ఈ ఇన్పుట్‌ను విశ్లేషించి తెలుగులో స్పందించండి. {prompt}",
    'kn': f"ದಯವಿಟ್ಟು ಈ ಇನ್‌ಪುಟ್ ಅನ್ನು ವಿಶ್ಲೇಷಿಸಿ ಮತ್ತು ಕನ್ನಡದಲ್ಲಿ ಪ್ರತಿಕ್ರಿಯೆ ನೀಡಿ. {prompt}",
    'ml': f"ഈ ഇൻപുട്ട് വിശകലനം ചെയ്ത് മലയാളത്തിൽ പ്രതികരിക്കൂ. {prompt}",
    'pa': f"ਕਿਰਪਾ ਕਰਕੇ ਇਸ ਇਨਪੁੱਟ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ ਅਤੇ ਪੰਜਾਬੀ ਵਿੱਚ ਜਵਾਬ ਦਿਓ। {prompt}",
    'or': f"ଦୟାକରି ଏହି ଇନପୁଟ୍‌କୁ ବିଶ୍ଲେଷଣ କରନ୍ତୁ ଏବଂ ଓଡ଼ିଆରେ ପ୍ରତିକ୍ରିୟା ଦିଅ। {prompt}",
    'en': f"Please analyze this input and respond in English. {prompt}",
    }


    return localized_templates.get(language_code, f"Please analyze this image and respond in English. {prompt}")

@cow_breed_bp.route('/api/new_chat', methods=['POST'])
def new_chat():
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        session_id = data.get('session_id', f"session_{len(chat_sessions) + 1}")

        session_key = f"{user_id}_{session_id}"

        chat_sessions[session_key] = model.start_chat(history=[])
        chat_sessions[session_key].send_message(SYSTEM_PROMPT, stream=False)

        return jsonify({
            'session_id': session_id,
            'message': 'New chat session created'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cow_breed_bp.route('/api/chat_history', methods=['GET'])
def get_chat_history():
    try:
        user_id = request.args.get('user_id', 'default_user')
        session_id = request.args.get('session_id', 'default_session')

        session_key = f"{user_id}_{session_id}"

        if session_key not in chat_sessions:
            return jsonify({'error': 'Chat session not found'}), 404

        chat = chat_sessions[session_key]

        history = []
        for message in chat.history:
            if message.role == "user" or (message.role == "model" and message.parts[0] != SYSTEM_PROMPT):
                history.append({
                    'role': message.role,
                    'content': message.parts[0] if isinstance(message.parts[0], str) else "image"
                })

        return jsonify({'history': history})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
