from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from openai import OpenAI
from pathlib import Path
import os
import datetime
import json
import uuid
import shutil

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure MySQL
app.config['MYSQL_HOST'] = os.getenv('host')
app.config['MYSQL_USER'] = os.getenv('user')
app.config['MYSQL_PASSWORD'] = os.getenv('password')
app.config['MYSQL_DB'] = os.getenv('database')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# Initialize the OpenAI client
openai_api_key = os.getenv('apikey')
client = OpenAI(api_key=openai_api_key)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(id=user['id'], username=user['username'], password=user['password'])
    return None

def check_spelling_and_grammar(text):
    """Check spelling and grammar using OpenAI GPT-4."""
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Please check the following text for any spelling or grammatical errors and suggest corrections."},
            {"role": "user", "content": text}
        ]
    )
    return completion.choices[0].message.content

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cursor.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        if user and check_password_hash(user['password'], password):
            login_user(User(id=user['id'], username=user['username'], password=user['password']))
            return redirect(url_for('index'))
        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/new_conversation')
@login_required
def new_conversation():
    session.pop('messages', None)
    session.pop('conversation_id', None)
    return redirect(url_for('index'))

@app.route('/load_conversations', methods=['GET'])
@login_required
def load_conversations():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT DISTINCT conversation_id, timestamp FROM sessions WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s OFFSET %s", (current_user.id, per_page, (page - 1) * per_page))
    conversations = cursor.fetchall()
    cursor.execute("SELECT COUNT(DISTINCT conversation_id) AS total FROM sessions WHERE user_id = %s", (current_user.id,))
    total = cursor.fetchone()['total']
    cursor.close()
    next_url = url_for('load_conversations', page=page + 1) if (page * per_page) < total else None
    prev_url = url_for('load_conversations', page=page - 1) if page > 1 else None
    return render_template('conversations.html', conversations=conversations, next_url=next_url, prev_url=prev_url)

@app.route('/load_conversation/<conversation_id>')
@login_required
def load_conversation(conversation_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT messages FROM sessions WHERE user_id = %s AND conversation_id = %s", (current_user.id, conversation_id))
    session_data = cursor.fetchone()
    cursor.close()
    if session_data:
        session['messages'] = json.loads(session_data['messages'])
        session['conversation_id'] = conversation_id
    return redirect(url_for('index'))

@app.route('/delete_conversation/<conversation_id>', methods=['POST'])
@login_required
def delete_conversation(conversation_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM sessions WHERE user_id = %s AND conversation_id = %s", (current_user.id, conversation_id))
    mysql.connection.commit()
    cursor.close()
    flash('Conversation deleted successfully.', 'success')
    return redirect(url_for('load_conversations'))

@app.route('/', methods=['GET', 'POST'])
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

    if request.method == 'POST':
        user_prompt = request.form['prompt']

        if user_prompt.lower() == 'exit':
            return render_template('audio.html', messages=messages, correction=correction)
        
        # Check spelling and grammar
        correction = check_spelling_and_grammar(user_prompt)

        messages.append({"role": "user", "content": user_prompt, "username": current_user.username, "correction": correction})

        # Generate a completion using the user's question
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": message["role"], "content": message["content"]} for message in messages]
        )
        # Get the response and print it
        model_response = completion.choices[0].message.content
        print(model_response)

        # Create directory for saving the audio file
        user_id = current_user.id
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        audio_dir = Path(app.root_path) / f"static/audio/{user_id}/{conversation_id}/{timestamp}"
        audio_dir.mkdir(parents=True, exist_ok=True)

        # Create speech from the response
        speech_file_name = f"speech_{timestamp}.mp3"
        speech_file_path = audio_dir / speech_file_name
        tts_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=model_response
        )
        tts_response.stream_to_file(speech_file_path)

        # Add the response to the messages as an Assistant Role
        messages.append({"role": "assistant", "content": model_response, "audio_file": str(speech_file_path.relative_to(app.root_path / "static"))})

        # Save session to database with timestamp
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO sessions (user_id, conversation_id, messages, timestamp) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE messages = VALUES(messages), timestamp = VALUES(timestamp)
        """, (current_user.id, conversation_id, json.dumps(messages), timestamp))
        mysql.connection.commit()
        cursor.close()

        # Update the session
        session['messages'] = messages
        session['conversation_id'] = conversation_id
    
    return render_template('audio.html', messages=messages, correction=correction)


if __name__ == '__main__':
    app.run(debug=True)
