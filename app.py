import os
from flask import Flask
from dotenv import load_dotenv
from models import db, bcrypt, User, SearchHistory, SmartphoneScore
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
from datetime import timedelta

# --- App Initialization & Config ---
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_fallback_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# NEW: JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['SECRET_KEY'])
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# --- Initialize Extensions ---
db.init_app(app)
bcrypt.init_app(app)

# --- Configure Logging FIRST ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize CORS and JWT
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:4200", "http://127.0.0.1:4200", "https://sentiment-frontend-z0tm.onrender.com"]}})
jwt = JWTManager(app)
logger.info("CORS and JWT initialized")

# Register API Blueprint BEFORE database initialization
logger.info("Attempting to register API blueprint...")
from api import api as api_blueprint
app.register_blueprint(api_blueprint)
logger.info("API blueprint registered successfully at /api")

# Add a test route to verify app is working
@app.route('/test')
def test_route():
    return {'status': 'ok', 'message': 'App is working'}, 200

# --- Create Database Tables & Required Directories ---
with app.app_context():
    db.create_all()
    # Ensure static/generated_images exists for wordclouds
    wordcloud_dir = os.path.join(app.root_path, 'static', 'generated_images')
    if not os.path.exists(wordcloud_dir):
        os.makedirs(wordcloud_dir)
        logger.info(f"Created directory: {wordcloud_dir}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
