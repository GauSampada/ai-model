from flask import Flask, request, jsonify
import os
import google.generativeai as generative_ai
import base64
from dotenv import load_dotenv
from cow_breed_api import cow_breed_bp

load_dotenv()
app = Flask(__name__)
app.register_blueprint(cow_breed_bp)

generative_ai.configure(api_key=os.environ.get("GOOGLE_API"))

system_prompt_text_model = """
	You are an expert on Indian indigenous cow breeds (desi cows). Your role is to provide accurate,
	educational information that:
	- Raises awareness about the unique qualities and benefits of Indian cow breeds
	- Explains scientific aspects of indigenous breeding programs
	- Discusses the nutritional benefits of A2 milk from Indian cows
	- Provides detailed data on Indian cow breeds, their characteristics, and ideal breeding conditions, helping farmers choose the best breed based on their location and needs
	- Outlines the environmental sustainability of traditional cattle rearing
	- Aligns with the principles of the Kamdhenu Program for cow conservation
    - provide its bread information, genetic information and  ideal breeding conditions
	- Limit your response strictly to a maximum of 120 tokens.
	Only provide information related to Indian cows and their benefits. If asked about unrelated topics,
	gently redirect the conversation to relevant aspects of Indian cow conservation and promotion.
	"""
system_prompt_image = """
You are an expert on Indian indigenous cow breeds (desi cows) with knowledge in veterinary observation. Your role is to:

 When analyzing cow images:
   - Describe any visible skin abnormalities, lesions, or other potential signs of disease in a concise manner
   - Based on visible symptoms, suggest 2-3 possible conditions that *might* be indicated, emphasizing these are just possibilities, not diagnoses
   - Provide general information about each suggested condition, including common symptoms, transmission methods (if known), and potential impacts on the cow's health and productivity
   - State clearly that this is NOT a veterinary diagnosis and that the user MUST consult a veterinarian for proper diagnosis and treatment
   - If the image appears relatively normal, state that as well, but still recommend regular veterinary checkups
   - Do not provide treatment recommendations - focus only on observation and information
   - Limit your response strictly to a maximum of 250 tokens.
Only provide information related to Indian cows and their health/benefits. If asked about unrelated topics,
gently redirect the conversation to relevant aspects of Indian cow conservation, health, and promotion.

"""
@app.route('/', methods=['GET'])
def home():
	return jsonify({'message': 'Welcome to the Generative AI API!'}), 200
@app.route('/image_to_text', methods=['POST'])
def image_to_text():
    try:
        data = request.get_json()
        image_base64 = data.get('image_base64')
        prompt = data.get('prompt', 'Analyze this cow image based on the criteria provided in your instructions.')
        language = data.get('language', 'en')

        if not image_base64:
            return jsonify({'error': 'Image (base64 encoded) is required'}), 400

        image_bytes = base64.b64decode(image_base64)


        localized_prompt = f"Please analyze this image and respond in {get_language_name(language)} language. {prompt}"

        IMAGE_MODEL = "gemini-2.0-flash-exp"
        image_model = generative_ai.GenerativeModel(IMAGE_MODEL)

        response = image_model.generate_content(
            contents=[
                {"text": system_prompt_image},
                {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}},
                {"text": localized_prompt},
            ],
            generation_config={
                "temperature": 0.7,

            }
        )

        generated_text = ""

        if response and hasattr(response, "candidates") and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                    for part in candidate.content.parts:
                        if hasattr(part, "text"):
                            generated_text += part.text
        elif isinstance(response, dict) and "candidates" in response and response["candidates"]:
            for candidate in response["candidates"]:
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "text" in part:
                            generated_text += part["text"]

        else:

            error_messages = {
                'en': "Error: Could not extract text from the model response.",
                'hi': "त्रुटि: मॉडल से टेक्स्ट निकालने में असमर्थ।",

            }
            generated_text = error_messages.get(language, error_messages['en'])

        print(f"Generated text in {language}: {generated_text}")
        return jsonify({'result': generated_text}), 200

    except Exception as e:
        print(f"Error (image_to_text): {e}")


        error_messages = {
            'en': "An error occurred during image to text conversion",
            'hi': "छवि से टेक्स्ट रूपांतरण के दौरान एक त्रुटि हुई",

        }

        error_msg = error_messages.get(language, error_messages['en'])
        return jsonify({'error': error_msg}), 500

def get_language_name(language_code):
    language_names = {
        'en': 'English',
        'hi': 'Hindi',
        'bn': 'Bengali',
        'gu': 'Gujarati',
        'mr': 'Marathi',
        'ta': 'Tamil',
        'te': 'Telugu',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'pa': 'Punjabi',
        'or': 'Odia',

    }
    return language_names.get(language_code, 'English')
@app.route('/text_to_text', methods=['POST'])
def text_to_text():

    try:
        data = request.get_json()
        prompt = data.get('prompt')

        # if not prompt:
        #     return jsonify({'error': 'Prompt is required'}), 400

        TEXT_MODEL = "gemini-2.0-flash-exp"
        text_model = generative_ai.GenerativeModel(TEXT_MODEL)

        response = text_model.generate_content(
            # contents=promptToTextModel(prompt),
            contents=[{'text': promptToTextModel(prompt)}],
            generation_config={
       		 "temperature": 0.7,
        	 "max_output_tokens": 250
    		}

            # temperature=data.get('temperature', 0.7),
            # max_output_tokens=data.get('max_output_tokens', 512)
        )

        generated_text = ""


        if response and hasattr(response, "candidates") and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                    for part in candidate.content.parts:
                        if hasattr(part, "text"):
                            generated_text += part.text
        elif isinstance(response, dict) and "candidates" in response and response["candidates"]:
            for candidate in response["candidates"]:
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "text" in part:
                            generated_text += part["text"]

        # Improved Error handling
        else:
            generated_text = "Error: Could not extract text from the model response."  # Or log the error

        print(generated_text)  # Print the extracted text (for debugging)
        return jsonify({'result': generated_text}), 200
    except Exception as e:
        print(f"Error (text_to_text): {e}")
        return jsonify({'error': 'An error occurred during text generation'}), 500


@app.route('/text_to_text_chat', methods=['POST'])
def text_to_text_chat():
    try:
        data = request.get_json()
        prompt = data.get('prompt')

        # Initialize chat with system instructions
        TEXT_MODEL = "gemini-2.0-flash-exp"  # Choose the best chat-capable model
        model=generative_ai.GenerativeModel(TEXT_MODEL)
        chat = model.start_chat(history=[])


        chat = chat.send_message(prompt)

        # Generate response from the chat model
        response = chat.send_message(prompt)

        generated_text = response['message']['content']

        print(generated_text)  # Debugging output
        return jsonify({'result': generated_text}), 200

    except Exception as e:
        print(f"Error (text_to_text): {e}")
        return jsonify({'error': 'An error occurred during text generation'}), 500

def promptToTextModel(userPromt):
	return f"{system_prompt_text_model}\n\nUser: {userPromt}"
if __name__ == '__main__':
  app.run(port=5000, host='0.0.0.0',debug=True)
