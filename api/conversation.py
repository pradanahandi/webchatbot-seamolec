from flask import request, jsonify, Blueprint, session, current_app
from flask_login import login_required, current_user
import uuid, datetime, json
from pathlib import Path
from .utils import check_spelling_and_grammar, save_audio, mysql

conversation_bp = Blueprint('conversation', __name__)

@conversation_bp.route('/new', methods=['POST'])
@login_required
def new_conversation():
    session.pop('messages', None)
    session.pop('conversation_id', None)
    return jsonify({"message": "New conversation started."}), 200

@conversation_bp.route('/load', methods=['GET'])
@login_required
def load_conversations():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT DISTINCT conversation_id, timestamp FROM sessions WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s OFFSET %s", 
                   (current_user.id, per_page, (page - 1) * per_page))
    conversations = cursor.fetchall()
    cursor.execute("SELECT COUNT(DISTINCT conversation_id) AS total FROM sessions WHERE user_id = %s", (current_user.id,))
    total = cursor.fetchone()['total']
    cursor.close()
    return jsonify({"conversations": conversations, "total": total}), 200

@conversation_bp.route('/load/<conversation_id>', methods=['GET'])
@login_required
def load_conversation(conversation_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT messages FROM sessions WHERE user_id = %s AND conversation_id = %s", (current_user.id, conversation_id))
    session_data = cursor.fetchone()
    cursor.close()
    if session_data:
        session['messages'] = json.loads(session_data['messages'])
        session['conversation_id'] = conversation_id
    return jsonify({"message": "Conversation loaded."}), 200

@conversation_bp.route('/delete/<conversation_id>', methods=['DELETE'])
@login_required
def delete_conversation(conversation_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM sessions WHERE user_id = %s AND conversation_id = %s", (current_user.id, conversation_id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Conversation deleted successfully."}), 200

@conversation_bp.route('/', methods=['POST'])
@login_required
def index():
    if 'messages' not in session:
        session['messages'] = [
            {"role": "system", "content": "Your responses should not exceed one sentence in length."}
        ]
    correction = None
    messages = session['messages']
    conversation_id = session.get('conversation_id')

    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        session['conversation_id'] = conversation_id

    user_prompt = request.json.get('prompt')
    
    if user_prompt.lower() == 'exit':
        return jsonify({"messages": messages, "correction": correction})

    # Check spelling and grammar
    correction = check_spelling_and_grammar(user_prompt)

    messages.append({"role": "user", "content": user_prompt, "username": current_user.username, "correction": correction})

    # Generate a completion using the user's question
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": message["role"], "content": message["content"]} for message in messages]
    )
    model_response = completion.choices[0].message.content

    # Create speech from the response
    speech_file_path = save_audio(current_user.id, conversation_id, model_response)

    # Add the response to the messages as an Assistant Role
    messages.append({"role": "assistant", "content": model_response, "audio_file": str(speech_file_path)})

    # Save session to database with timestamp
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO sessions (user_id, conversation_id, messages, timestamp) 
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE messages = VALUES(messages), timestamp = VALUES(timestamp)
    """, (current_user.id, conversation_id, json.dumps(messages), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    mysql.connection.commit()
    cursor.close()

    session['messages'] = messages
    session['conversation_id'] = conversation_id

    return jsonify({"messages": messages, "correction": correction})
