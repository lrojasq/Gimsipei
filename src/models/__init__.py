# Import all models to ensure SQLAlchemy can resolve relationships
from .user import User, UserRole
from .document import Document
from .subject import Subject
from .class_model import ClassModel
from .class_view import ClassView
from .resource import Resource
from .book import Book
from .course import Course
from .course_student import CourseStudent
from .course_subject import CourseSubject
from .evaluation import Evaluation
from .evaluation_question import EvaluationQuestion, QuestionType
from .evaluation_question_option import EvaluationQuestionOption
from .evaluation_submission import EvaluationSubmission
from .evaluation_submission_answer import EvaluationSubmissionAnswer

__all__ = [
    "User",
    "UserRole",
    "Document",
    "Subject",
    "ClassModel",
    "ClassView",
    "Resource",
    "Book",
    "Course",
    "CourseStudent",
    "CourseSubject",
    "Evaluation",
    "EvaluationQuestion",
    "QuestionType",
    "EvaluationQuestionOption",
    "EvaluationSubmission",
    "EvaluationSubmissionAnswer",
]
