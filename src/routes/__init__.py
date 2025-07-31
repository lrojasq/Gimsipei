from src.book.router import book_bp
from src.auth.router import auth_bp
from src.users.router import users_bp

# Importa aquí otros blueprints si los tienes, por ejemplo:
# from .auth import auth_bp
# from .documents import documents_bp


def register_blueprints(app):
    app.register_blueprint(book_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    # app.register_blueprint(documents_bp)
    # ...otros blueprints...
