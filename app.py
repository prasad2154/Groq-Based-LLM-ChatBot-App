import os
import json
import logging
import threading
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from llama_index.llms.groq import Groq as LlamaGroq
from llama_index.core.llms import ChatMessage, MessageRole
from uuid import uuid4

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder=None)
CORS(app)

# Session Management: Stores history as LlamaIndex ChatMessage compatible dicts
session_histories = {}
history_lock = threading.Lock()

def initialize_session_history(session_id):
    with history_lock:
        if session_id not in session_histories:
            session_histories[session_id] = []  # Store list of dicts: {"role": ..., "content": ...}
            logging.info(f"Initialized history for new session: {session_id}")
        return session_histories[session_id]

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/create-session', methods=['POST'])
def create_session_route():
    try:
        session_id = str(uuid4())
        initialize_session_history(session_id)
        logging.info(f"New backend session created: {session_id}")
        return jsonify({'status': 'success', 'session_id': session_id}), 200
    except Exception as e:
        logging.error(f"Error in /create-session: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/clear-backend-history', methods=['POST'])
def clear_backend_history_route():
    data = request.json
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'status': 'error', 'message': 'session_id is required'}), 400

    with history_lock:
        if session_id in session_histories:
            session_histories[session_id] = []
            logging.info(f"Backend chat history cleared for session: {session_id}")
            message = 'Backend chat history cleared for this session.'
        else:
            # It's okay if the session wasn't on backend yet, initialize it empty.
            initialize_session_history(session_id)
            logging.warning(f"Attempted to clear history for session not actively on backend (or new): {session_id}. Initialized empty.")
            message = 'Backend session history was not found (or was new) and is now initialized empty.'
            
    return jsonify({'status': 'success', 'message': message})


def generate_chat_stream_with_session(payload):
    session_id = payload.get('session_id')
    user_prompt_text = payload.get('prompt')
    system_prompt_text = payload.get('system_prompt', "").strip() # Default to empty if not provided
    temperature = float(payload.get('temperature', 0.7))
    model_id = payload.get('model_id', 'openai/gpt-oss-20b')

    if not session_id:
        yield f"data: {json.dumps({'error': 'session_id is required for backend history', 'is_final': True})}\n\n"
        return
    if not user_prompt_text:
        yield f"data: {json.dumps({'error': 'Prompt is required', 'is_final': True})}\n\n"
        return

    api_key_to_use = os.environ.get("GROQ_API_KEY")
    # If you must use a hardcoded key for testing and GROQ_API_KEY is not set:
    # if not api_key_to_use:
    #     api_key_to_use = "gsk_YOUR_GROQ_API_KEY" # Replace with your actual key if needed for testing

    if not api_key_to_use:
        logging.error("GROQ_API_KEY not found in environment variables.")
        yield f"data: {json.dumps({'error': 'GROQ_API_KEY not configured on server.', 'is_final': True})}\n\n"
        return

    try:
        llm = LlamaGroq(model=model_id, api_key=api_key_to_use)
        
        messages_for_llm = []
        with history_lock:
            # Retrieve current history for the session (list of dicts)
            current_history_dicts = list(session_histories.get(session_id, [])) # Make a copy

            # Handle System Prompt:
            # Prepend system prompt if provided and not already the first message, or if history is empty.
            # This allows changing system prompt mid-conversation to take effect.
            if system_prompt_text:
                if not current_history_dicts or current_history_dicts[0].get("role") != MessageRole.SYSTEM:
                    messages_for_llm.append(ChatMessage(role=MessageRole.SYSTEM, content=system_prompt_text))
                elif current_history_dicts[0].get("role") == MessageRole.SYSTEM and current_history_dicts[0].get("content") != system_prompt_text:
                    # If system prompt exists but changed, replace it
                    current_history_dicts[0]["content"] = system_prompt_text # Update history for next time
                    messages_for_llm.append(ChatMessage(role=MessageRole.SYSTEM, content=system_prompt_text))


            # Convert stored history dicts to ChatMessage objects
            for msg_dict in current_history_dicts:
                # Avoid adding system message again if already handled
                if msg_dict.get("role") == MessageRole.SYSTEM and messages_for_llm and messages_for_llm[0].role == MessageRole.SYSTEM:
                    continue
                messages_for_llm.append(ChatMessage(role=MessageRole(msg_dict["role"]), content=str(msg_dict["content"])))
        
        # Add current user prompt
        user_chat_message = ChatMessage(role=MessageRole.USER, content=user_prompt_text)
        messages_for_llm.append(user_chat_message)

        logging.info(f"Session {session_id} - Calling LLM '{model_id}' with {len(messages_for_llm)} messages. System: '{system_prompt_text[:30]}...', User: '{user_prompt_text[:50]}...'")

        stream_resp = llm.stream_chat(messages_for_llm, temperature=temperature)

        full_response_content = ""
        for r_chunk in stream_resp:
            delta_content = r_chunk.delta
            if delta_content:
                full_response_content += delta_content
                yield f"data: {json.dumps({'text_chunk': delta_content, 'is_final': False})}\n\n"
        
        # Persist messages to session history
        with history_lock:
            # Ensure session_id key exists
            if session_id not in session_histories:
                 initialize_session_history(session_id)

            # Update system prompt in history if it was added/changed
            if system_prompt_text:
                if not session_histories[session_id] or session_histories[session_id][0].get("role") != MessageRole.SYSTEM:
                    session_histories[session_id].insert(0, {"role": MessageRole.SYSTEM, "content": system_prompt_text})
                elif session_histories[session_id][0].get("role") == MessageRole.SYSTEM and session_histories[session_id][0].get("content") != system_prompt_text:
                     session_histories[session_id][0]["content"] = system_prompt_text


            session_histories[session_id].append({"role": MessageRole.USER, "content": user_prompt_text})
            session_histories[session_id].append({"role": MessageRole.ASSISTANT, "content": full_response_content})
            # Optional: Limit history size to prevent excessive memory usage
            # MAX_HISTORY_LEN = 50 # Example: keep last 50 messages (25 pairs)
            # if len(session_histories[session_id]) > MAX_HISTORY_LEN:
            #     session_histories[session_id] = session_histories[session_id][-MAX_HISTORY_LEN:]


        logging.info(f"Session {session_id} - LLM full response length: {len(full_response_content)}. History size: {len(session_histories.get(session_id, []))}")
        yield f"data: {json.dumps({'full_response': full_response_content, 'is_final': True})}\n\n"

    except Exception as e:
        logging.error(f"Error in Groq stream for session {session_id}: {e}", exc_info=True)
        yield f"data: {json.dumps({'error': f'LLM Error: {str(e)}', 'is_final': True})}\n\n"


@app.route('/chat', methods=['POST'])
def chat_route_post():
    payload = request.json
    session_id = payload.get('session_id')
    
    # Ensure session history is initialized on the backend if accessed directly
    # (though frontend should call /create-session first)
    if session_id:
        initialize_session_history(session_id) 
    else: # Should not happen if frontend is working correctly
        logging.error("Chat request received without session_id in payload.")
        # Fallback: create one, but this indicates a frontend issue
        # session_id = str(uuid4())
        # initialize_session_history(session_id)
        # payload['session_id'] = session_id 
        # This part is risky as frontend won't know this session_id for subsequent calls
        # Better to error out if session_id is missing and expected.
        # For now, generate_chat_stream_with_session will handle the error.
        pass
        
    return Response(generate_chat_stream_with_session(payload), mimetype='text/event-stream')

if __name__ == '__main__':
    if not os.environ.get("GROQ_API_KEY"):
        # This is the API key from your new app.py. 
        # For security, it's best to set GROQ_API_KEY as an environment variable.
        # Example: export GROQ_API_KEY="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"
        logging.warning("GROQ_API_KEY not found in environment variables. LLM calls might fail or use a test key if hardcoded (not recommended for production).")
    app.run(debug=True, host='0.0.0.0', port=5000)