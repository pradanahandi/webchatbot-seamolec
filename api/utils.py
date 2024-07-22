from flask_login import UserMixin
from flask_mysqldb import MySQL
import os
import datetime
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

mysql = MySQL()
openai_api_key = os.getenv('apikey')
client = OpenAI(api_key=openai_api_key)

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

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

def save_audio(user_id, conversation_id, text):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    audio_dir = Path("static/audio") / str(user_id) / str(conversation_id) / timestamp
    audio_dir.mkdir(parents=True, exist_ok=True)
    speech_file_name = f"speech_{timestamp}.mp3"
    speech_file_path = audio_dir / speech_file_name
    tts_response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    tts_response.stream_to_file(speech_file_path)
    return speech_file_path

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(id=user['id'], username=user['username'], password=user['password'])
    return None
