# Indian Indigenous Cow Breed AI API

## Introduction
This project provides an AI-powered API for analyzing Indian indigenous cow breeds (desi cows). It utilizes Google's Gemini AI models to process both text and image-based inputs, offering insights into cow breeds, breeding programs, A2 milk benefits, and basic veterinary observations. The API is designed to help farmers, researchers, and enthusiasts gain knowledge about Indian cow breeds and their health conditions.

## Features
- **Image Analysis:** Accepts a base64-encoded image of a cow and provides observations about potential health conditions based on visible symptoms.
- **Text-Based Querying:** Provides information on Indian cow breeds, breeding conditions, A2 milk benefits, and conservation programs.
- **Chat-Based Interaction:** Supports interactive conversations about Indian cow breeds.

## Installation
To set up the project locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/GauSampada/ai-model
   cd ai-model
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Create a `.env` file in the project directory and add:
     ```
     GOOGLE_API_KEY=your_google_api_key
     ```

## Usage

### Start the Flask Application
Run the Flask app using:
```bash
python app.py
```
This will start the API on `http://0.0.0.0:5000`.

### API Endpoints

#### 1. Home
- **Endpoint:** `/`
- **Method:** `GET`
- **Description:** Returns a welcome message.

#### 2. Image Analysis
- **Endpoint:** `/image_to_text`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "image_base64": "<base64-encoded-image>",
    "prompt": "Analyze this cow image."
  }
  ```
- **Response:** AI-generated insights about the cow’s health.

#### 3. Text Query
- **Endpoint:** `/text_to_text`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "prompt": "Tell me about Gir cows."
  }
  ```
- **Response:** Detailed information about Indian cow breeds.

#### 4. Chat-based Query
- **Endpoint:** `/text_to_text_chat`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "prompt": "Which Indian cow breed is best for milk production?"
  }
  ```
- **Response:** AI-powered interactive chat response.

## Contributing
We welcome contributions! To contribute:
1. Fork the repository.
2. Create a new branch for your feature.
3. Commit your changes with clear messages.
4. Push to your branch and create a pull request.

---
*This project leverages Google's Gemini AI for content generation and analysis.*

