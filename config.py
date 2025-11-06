# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()


# class Config:
#     # Flask basic configuration
#     SECRET_KEY = os.getenv("SECRET_KEY")

#     # Database configuration
#     SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

#     # File upload configuration
#     MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max size
#     UPLOAD_EXTENSIONS = [".epub", ".jpg", ".jpeg", ".png", ".webp"]
#     PRESERVE_CONTEXT_ON_EXCEPTION = False

#     # JWT Configuration
#     JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
#     JWT_TOKEN_LOCATION = ["headers", "cookies"]  # Soporta tanto headers como cookies
#     JWT_COOKIE_SECURE = False  # Set to True in production
#     JWT_COOKIE_CSRF_PROTECT = False  # Deshabilitado para simplificar
#     JWT_ACCESS_COOKIE_PATH = "/"
#     JWT_REFRESH_COOKIE_PATH = "/auth/refresh"
#     JWT_COOKIE_SAMESITE = "Lax"

#     # JWT expiration configuration (in seconds)
#     JWT_ACCESS_TOKEN_EXPIRES = 2 * 60 * 60  # 2 hours
#     JWT_REFRESH_TOKEN_EXPIRES = 5 * 24 * 60 * 60  # 5 days

#     # Server configuration
#     PORT = int(os.getenv("PORT", 5000))
#     FLASK_ENV = os.getenv("FLASK_ENV", "development")
import os
from dotenv import load_dotenv

# Cargar variables desde el archivo .env
load_dotenv()

class Config:
    # =======================
    # Flask basic configuration
    # =======================
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")

    # =======================
    # Database configuration
    # =======================
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =======================
    # File upload configuration
    # =======================
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max size
    UPLOAD_EXTENSIONS = [".epub", ".jpg", ".jpeg", ".png", ".webp"]
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    # =======================
    # JWT Configuration
    # =======================
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback_jwt_secret")
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = False  # True en producción con HTTPS
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/auth/refresh"
    JWT_COOKIE_SAMESITE = "Lax"

    # Expiración de tokens (en segundos)
    JWT_ACCESS_TOKEN_EXPIRES = 2 * 60 * 60  # 2 horas
    JWT_REFRESH_TOKEN_EXPIRES = 5 * 24 * 60 * 60  # 5 días

    # =======================
    # Server configuration
    # =======================
    PORT = int(os.getenv("PORT", 5010))
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
