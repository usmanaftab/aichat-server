from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.chat import Chat
import requests
import uuid

chat = Blueprint('chat', __name__)

@chat.route('/send', methods=['POST'])
@jwt_required()
def send_chat():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400

        # Get or create chat context
        context_id = data.get('context_id')
        if context_id:
            chat_session = Chat.objects(context_id=context_id, user_id=user_id).first()
            if not chat_session:
                return jsonify({'error': 'Invalid context ID'}), 404
        else:
            context_id = str(uuid.uuid4())
            chat_session = Chat(user_id=user_id, context_id=context_id)
            chat_session.save()

        # Build context from previous messages
        context = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in chat_session.messages
        ])
        
        # Prepare prompt with context
        full_prompt = f"{context}\nUser: {data['message']}\nAssistant:"

        # Ollama API endpoint
        ollama_url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3.2",
            "prompt": full_prompt,
            "stream": False
        }

        # Send request to Ollama
        response = requests.post(ollama_url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', '')

            # Save messages to context
            chat_session.messages.append({
                'role': 'user',
                'content': data['message']
            })
            chat_session.messages.append({
                'role': 'assistant',
                'content': ai_response
            })
            chat_session.save()

            return jsonify({
                'response': ai_response,
                'context_id': context_id,
                'success': True
            })
        else:
            return jsonify({
                'error': 'Failed to get response from LLM',
                'status': response.status_code
            }), 500

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500 