from src.book.router import book_bp
from src.auth.router import auth_bp
from src.users.router import users_bp
from src.courses.router import courses_bp
from src.classes.routes import class_bp
from src.resources.router import resources_bp
from src.evaluations.router import evaluations_bp
from src.subject.router import subjects_bp
from src.grades.router import grades_bp


def register_blueprints(app):
    app.register_blueprint(book_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(class_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(evaluations_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(grades_bp)
