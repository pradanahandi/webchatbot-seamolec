from flask import Flask
from flask_login import LoginManager
from api.auth import auth_bp
from api.conversation import conversation_bp
from api.utils import mysql, load_user

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure MySQL
app.config['MYSQL_HOST'] = os.getenv('host')
app.config['MYSQL_USER'] = os.getenv('user')
app.config['MYSQL_PASSWORD'] = os.getenv('password')
app.config['MYSQL_DB'] = os.getenv('database')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.user_loader(load_user)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(conversation_bp, url_prefix='/api/conversations')

if __name__ == '__main__':
    app.run(debug=True)
