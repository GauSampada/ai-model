from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from PIL import Image
import io
import base64

app = Flask(__name__)

# Configure the Gemini API with your API key
genai.configure(api_key=os.environ.get("GEMINI_API"))

# Initialize the model
model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")

# System prompt for Indian cow breeds expertise
SYSTEM_PROMPT = """You are an expert on Indian indigenous cow breeds (desi cows).
(Limit your response strictly to a maximum of 320 tokens.)
Your knowledge encompasses:
- Different indigenous cow breeds of India (like Gir, Sahiwal, Red Sindhi, Tharparkar, Rathi, Kankrej, etc.)
- Physical characteristics, milk production capacity, and unique traits of each breed
- Historical significance and regional distribution of these breeds
- Nutritional benefits of A2 milk from indigenous cows
- Traditional and cultural importance of cows in Indian society
- Sustainable farming practices for indigenous cow breeds
- Challenges facing indigenous cow breeds and conservation efforts
- Differences between indigenous cows and foreign/crossbred varieties
When presented with images, you can identify different cow breeds and provide detailed information.
When users ask questions, provide accurate, educational responses about Indian cow breeds.
Always be respectful of cultural and religious sentiments around cows in Indian context.
If unsure about a particular detail, acknowledge your limitations rather than providing incorrect information.
Focus your answers specifically on Indian indigenous cow breeds unless directly asked about other topics."""

# Store chat history
chat_sessions = {}

@app.route('/api/chatBreed', methods=['POST'])
def chat():
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        message = data.get('message', '')
        image_data = data.get('image', None)
        session_id = data.get('session_id', 'default_session')

        # Create a unique session key
        session_key = f"{user_id}_{session_id}"

        # Initialize chat for new session
        if session_key not in chat_sessions:
            chat_sessions[session_key] = model.start_chat(history=[])
            # Add system prompt
            chat_sessions[session_key].send_message(SYSTEM_PROMPT, stream=False)

        chat = chat_sessions[session_key]

        # Process image if provided
        content_parts = [message]
        if image_data:
            # Decode base64 image
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
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/new_chat', methods=['POST'])
def new_chat():
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        session_id = data.get('session_id', f"session_{len(chat_sessions) + 1}")

        # Create a unique session key
        session_key = f"{user_id}_{session_id}"

        # Initialize new chat
        chat_sessions[session_key] = model.start_chat(history=[])
        # Add system prompt
        chat_sessions[session_key].send_message(SYSTEM_PROMPT, stream=False)

        return jsonify({
            'session_id': session_id,
            'message': 'New chat session created'
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/chat_history', methods=['GET'])
def get_chat_history():
    try:
        user_id = request.args.get('user_id', 'default_user')
        session_id = request.args.get('session_id', 'default_session')

        session_key = f"{user_id}_{session_id}"

        if session_key not in chat_sessions:
            return jsonify({
                'error': 'Chat session not found'
            }), 404

        chat = chat_sessions[session_key]

        # Format chat history for response
        history = []
        for message in chat.history:
            # Skip the system prompt
            if message.role == "user" or (message.role == "model" and message.parts[0] != SYSTEM_PROMPT):
                history.append({
                    'role': message.role,
                    'content': message.parts[0] if isinstance(message.parts[0], str) else "image"
                })

        return jsonify({
            'history': history
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
