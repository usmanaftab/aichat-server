from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.chat import Chat
import requests
import uuid
from app.utils.request_limiter import check_request_quota
from app.models.request_quota import RequestQuota

chat = Blueprint('chat', __name__)

@chat.route('/send', methods=['POST'])
@jwt_required()
@check_request_quota
def send_chat():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400

        # Get remaining requests for response
        remaining_requests = RequestQuota.get_remaining_requests(user_id)

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

            # Save messages to context and set TTL
            chat_session.messages.append({
                'role': 'user',
                'content': data['message']
            })
            chat_session.messages.append({
                'role': 'assistant',
                'content': ai_response
            })
            chat_session.ttl = datetime.utcnow() + timedelta(days=2)
            chat_session.save()

            return jsonify({
                'response': ai_response,
                'context_id': context_id,
                'success': True,
                'quota': {
                    'remaining_requests': remaining_requests,
                    'max_requests': 15,
                    'reset_time': 'midnight UTC'
                }
            })
        else:
            return jsonify({
                'error': 'Failed to get response from LLM',
                'status': response.status_code,
                'quota': {
                    'remaining_requests': remaining_requests,
                    'max_requests': 15,
                    'reset_time': 'midnight UTC'
                }
            }), 500

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False,
            'quota': {
                'remaining_requests': RequestQuota.get_remaining_requests(user_id) - 1,
                'max_requests': 15,
                'reset_time': 'midnight UTC'
            }
        }), 500 