from flask import request, jsonify, Blueprint, current_app
from flask_mysqldb import MySQL
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .utils import User

auth_bp = Blueprint('auth', __name__)
mysql = MySQL()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = generate_password_hash(data['password'])
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Registration successful! Please log in."}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    if user and check_password_hash(user['password'], password):
        login_user(User(id=user['id'], username=user['username'], password=user['password']))
        return jsonify({"message": "Login successful!"}), 200
    return jsonify({"message": "Invalid credentials. Please try again."}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful!"}), 200
