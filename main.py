from flask import Flask, flash, jsonify, redirect, request, url_for
from flask_cors import CORS
from flask_jwt_extended import JWTManager, unset_jwt_cookies
from flask_migrate import Migrate

from config import Config
from src.database.database import Base
from src.models import *
from src.routes import register_blueprints

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


@jwt.unauthorized_loader
def handle_unauthorized(reason: str):
    """
    Se ejecuta cuando no se envía ningún token o falta el encabezado/cookie.
    - Si es una petición AJAX (fetch desde JS), respondemos JSON 401.
    - Para el resto, limpiamos cookies y redirigimos al login.
    """
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return (
            jsonify(
                {
                    "error": "authorization_required",
                    "message": "Autenticación requerida.",
                }
            ),
            401,
        )

    flash(
        "Tu sesión ha expirado o no estás autenticado. Inicia sesión nuevamente.",
        "warning",
    )
    response = redirect(url_for("auth.login"))
    unset_jwt_cookies(response)
    return response


@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    """
    Se ejecuta cuando el token JWT ha expirado.
    - Si es una petición AJAX, respondemos JSON 401.
    - Para el resto, limpiamos cookies y redirigimos al login.
    """
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return (
            jsonify(
                {
                    "error": "token_expired",
                    "message": "Tu sesión ha expirado. Vuelve a iniciar sesión.",
                }
            ),
            401,
        )

    flash("Tu sesión ha expirado. Por favor inicia sesión de nuevo.", "warning")
    response = redirect(url_for("auth.login"))
    unset_jwt_cookies(response)
    return response


@jwt.invalid_token_loader
def handle_invalid_token(reason: str):
    """
    Se ejecuta cuando el token es inválido (mal formado, firma incorrecta, etc.).
    Comportamiento similar a token expirado: limpiar sesión y enviar al login.
    """
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return (
            jsonify(
                {
                    "error": "invalid_token",
                    "message": "El token de sesión es inválido. Inicia sesión nuevamente.",
                }
            ),
            401,
        )

    flash("Tu sesión no es válida. Inicia sesión nuevamente.", "warning")
    response = redirect(url_for("auth.login"))
    unset_jwt_cookies(response)
    return response


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
