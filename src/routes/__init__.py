# from src.book.router import book_bp
from src.auth.router import auth_bp
from src.users.router import users_bp
from src.admin.router import admin_bp
from src.assignments.router import assignments_bp
from src.documents.router import documents_bp
from src.exercises.router import exercises_bp
from src.courses.router import courses_bp

# from src.academic.router import academic_bp
from src.subject.router import subjects_bp


def register_blueprints(app):
    # app.register_blueprint(book_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(exercises_bp)
    app.register_blueprint(courses_bp)
    # app.register_blueprint(academic_bp)
    app.register_blueprint(subjects_bp)
