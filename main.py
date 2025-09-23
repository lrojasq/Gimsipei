from flask import Flask, jsonify, redirect, url_for
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from src.routes import register_blueprints
from src.database.database import Base
from src.models import *
from config import Config

# Initialize Flask app
app = Flask(__name__, template_folder="src/templates", static_folder="src/static")

# Configure app using Config class
app.config.from_object(Config)

# Initialize extensions
jwt = JWTManager(app)
CORS(app)
migrate = Migrate(app, Base)

# Database tables are now managed by Flask-Migrate
# Base.metadata.create_all(bind=engine)  # Commented out - use migrations instead


def init_routes():
    register_blueprints(app)


# Error handlers
@app.route("/")
def index():
    return redirect(url_for("auth.login"))


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
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.FLASK_ENV == "development")
