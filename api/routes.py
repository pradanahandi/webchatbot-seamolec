from flask import request, jsonify
from flask_login import login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql
from . import api
import uuid
import json
import datetime

@api.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = generate_password_hash(data.get('password'))
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'Registration successful!'}), 201

@api.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    if user and check_password_hash(user['password'], password):
        login_user(User(id=user['id'], username=user['username'], password=user['password']))
        return jsonify({'message': 'Login successful!', 'user_id': user['id']}), 200
    return jsonify({'message': 'Invalid credentials.'}), 401

@api.route('/user', methods=['GET'])
@login_required
def user():
    return jsonify({'id': current_user.id, 'username': current_user.username}), 200

@api.route('/conversations', methods=['POST'])
@login_required
def new_conversation():
    conversation_id = str(uuid.uuid4())
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO sessions (user_id, conversation_id, messages, timestamp) VALUES (%s, %s, %s, %s)",
                   (current_user.id, conversation_id, json.dumps([]), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'New conversation created!', 'conversation_id': conversation_id}), 201

@api.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT DISTINCT conversation_id, timestamp FROM sessions WHERE user_id = %s ORDER BY timestamp DESC", (current_user.id,))
    conversations = cursor.fetchall()
    cursor.close()
    return jsonify(conversations), 200

@api.route('/conversations/<conversation_id>', methods=['GET'])
@login_required
def get_conversation(conversation_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT messages FROM sessions WHERE user_id = %s AND conversation_id = %s", (current_user.id, conversation_id))
    session_data = cursor.fetchone()
    cursor.close()
    if session_data:
        return jsonify({'messages': json.loads(session_data['messages'])}), 200
    return jsonify({'message': 'Conversation not found.'}), 404

@api.route('/conversations/<conversation_id>', methods=['DELETE'])
@login_required
def delete_conversation(conversation_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM sessions WHERE user_id = %s AND conversation_id = %s", (current_user.id, conversation_id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'Conversation deleted successfully.'}), 200
