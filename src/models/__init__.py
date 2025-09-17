# Import all models to ensure SQLAlchemy can resolve relationships
from .user import User, UserRole
from .document import Document
from .exercise import Exercise
from .assignment import Assignment
from .submission import Submission
from .subject import Subject
from .period import Period
from .class_model import ClassModel
from .class_view import ClassView
from .resource import Resource
from .book import Book
from .course import Course
from .course_student import CourseStudent
from .course_subject import CourseSubject

__all__ = [
    "User",
    "UserRole",
    "Document",
    "Exercise",
    "Assignment",
    "Submission",
    "Subject",
    "Period",
    "ClassModel",
    "ClassView",
    "Resource",
    "Book",
    "Course",
    "CourseStudent",
    "CourseSubject",
]
