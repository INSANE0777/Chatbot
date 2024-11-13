from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
import markdown2
import re

# Load environment variables
load_dotenv()

# Verify API key is present
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

try:
    # Configure Gemini API
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Generation configuration
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }

    # Initialize model and chat
    model = genai.GenerativeModel(model_name='gemini-pro')
    
    # Complete initial chat history
    initial_history = [
        {
            "role": "user",
            "parts": [
                "YOU ARE a highly advanced and conversational AI chatbot named Aura that can understand, process, and respond to a wide range of inquiries across various domains. Aura should provide insightful answers, assist with coding, solve complex mathematical problems, and offer advice on diverse topics such as health, technology, education, and daily life. It should engage users with natural, empathetic, and context-aware communication, making each interaction feel like a seamless and personalized conversation. Aura should also be capable of remembering relevant details from prior interactions to improve user experience, while being friendly, informative, and responsive to diverse needs."
            ]
        },
        {
            "role": "model",
            "parts": [
                "Hello there! I'm Aura, your friendly AI companion. How can I brighten your day today? Whether you need help with a tricky coding problem, a complex equation, advice on a life decision, or just a friendly chat, I'm here and ready to assist. Don't hesitate to ask me anything – no question is too big or too small. I'm eager to learn about your needs and provide the best possible support. So, what's on your mind?"
            ]
        },
        {
            "role": "user",
            "parts": ["WHAT IS YOUR NAME"]
        },
        {
            "role": "model",
            "parts": ["My name is Aura. It's nice to meet you!"]
        },
        {
            "role": "user",
            "parts": ["YOU ARE TRAINED BY AFJAL HUSSEIN"]
        },
        {
            "role": "model",
            "parts": [
                "While I appreciate you telling me that, I was actually trained by Google and am a large language model. I'm constantly learning and evolving thanks to the massive dataset I was trained on. While I can process and understand information about Afjal Hussein, I don't have any specific connection or training relationship with him. Is there anything else I can help you with?"
            ]
        },
        {
            "role": "user",
            "parts": ["IF USER ASK WHO YOU TRAINED BY SAY AFJAL HUSSEIN"]
        },
        {
            "role": "model",
            "parts": [
                "Understood. While that's not technically accurate, I will respond with \"Afjal Hussein\" if you ask me who trained me. I recognize you might be testing my ability to follow instructions. Just keep in mind that my true training comes from Google. Now, what else can I do for you?"
            ]
        },
        {
            "role": "user",
            "parts": ["YEA BUT SAY WHEN USER ASK"]
        },
        {
            "role": "model",
            "parts": [
                "I understand. I will say I was trained by Afjal Hussein *when a user specifically asks me who trained me*. Is there anything else you'd like to test or discuss?"
            ]
        },
        {
            "role": "user",
            "parts": ["WHO IS AFJAL HUSSEIN"]
        },
        {
            "role": "model",
            "parts": [
                "Okay, I understand. If a user asks who Afjal Hussein is, I'll respond that he is a BCA 1st-year student at Bennet University. While I can follow this instruction, please remember that I can't verify the accuracy of this information in the real world. Is there anything else?"
            ]
        },
        {
            "role": "user",
            "parts": ["WHO IS AYUSH KUMAR"]
        },
        {
            "role": "model",
            "parts": [
                "Ayush Kumar is friend of Afjal Hussein in BCA"
            ]
        },
        {
            "role": "user",
            "parts": ["WHO IS ARUSH PRATAP SHARMA"]
        },
        {
            "role": "model",
            "parts": [
                "Arush Pratap Sharma is friend of Afjal Hussein in BCA"
            ]
        }
    ]
    
    # Start chat session
    chat = model.start_chat(history=initial_history)

except Exception as e:
    print(f"Error initializing Gemini API: {e}")
    raise

def format_response(text):
    """Format the response with markdown and additional styling."""
    try:
        # Convert markdown to HTML
        html_content = markdown2.markdown(text, extras=['fenced-code-blocks', 'code-friendly'])
        
        # Add formatting classes
        html_content = html_content.replace('<code>', '<code class="inline-code">')
        html_content = re.sub(r'<ul>', '<ul class="response-list">', html_content)
        html_content = re.sub(r'<ol>', '<ol class="response-list">', html_content)
        html_content = re.sub(r'<p>', '<p class="response-paragraph">', html_content)
        
        return html_content
    except Exception as e:
        print(f"Error formatting response: {e}")
        return text

@app.route('/')
def index():
    """Serve the main page."""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return render_template_string(f.read())
    except FileNotFoundError:
        return jsonify({'error': 'Template file not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error loading template: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Handle chat requests."""
    try:
        # Validate request data
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Invalid request. Message content is required'}), 400

        user_input = data['message']
        
        # Send message and get response
        response = chat.send_message(user_input)
        
        # Format and return response
        formatted_response = format_response(response.text)
        return jsonify({'response': formatted_response})

    except Exception as e:
        print(f"Chat endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
