from flask import Flask, request,json, jsonify, current_app, render_template, redirect, url_for, flash, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import User, UserRole
from src.database.database import SessionLocal
from typing import Dict, Any, Union
import os
from functools import wraps

from src.routes import register_blueprints
from src.database.database import engine, Base

from src.routes import register_blueprints
from src.database.database import engine, Base

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder="src/templates", static_folder="src/static")

# Configure app
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# File upload configuration
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max size
app.config["UPLOAD_EXTENSIONS"] = [".epub", ".jpg", ".jpeg", ".png", ".webp"]
# Important configuration for correct file handling
app.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = False

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_COOKIE_SECURE"] = False  # Set to True in production
app.config["JWT_COOKIE_CSRF_PROTECT"] = True
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
app.config["JWT_REFRESH_COOKIE_PATH"] = "/auth/refresh"
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
# JWT expiration configuration (in seconds)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 2 * 60 * 60  # 2 hours
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 5 * 24 * 60 * 60  # 5 days

# Initialize extensions
jwt = JWTManager(app)
CORS(app)

# Import models
from src.models.user import User
from src.models.document import Document
from src.models.exercise import Exercise
from src.models.assignment import Assignment
from src.models.submission import Submission
from src.models.subject import Subject
from src.models.period import Period
from src.models.class_model import ClassModel
from src.models.class_view import ClassView
from src.models.resource import Resource

# Create database tables
Base.metadata.create_all(bind=engine)


def init_routes():
    register_blueprints(app)


# Error handlers
@app.route('/')
@app.route('/auth/login')
def index():
    return render_template('auth/login.html')


@app.route('/auth/user', methods=['GET','POST'])
def user() -> Union[str, tuple[Dict[str, Any], int]]:
    return render_template('admin/user.html')

# @app.route('/auth/subcategoria')
# def subcategoria():
#     return render_template('subCategory/clases/subcategoria.html')

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# Health check endpoint
@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"}), 200


# Initialize routes
init_routes()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5010))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_ENV") == "development")
