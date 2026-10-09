"""Seed the test database with realistic data (~10% of production size).

Production baseline (modulo_gimsipei, READ ONLY — never written from here):
  29 users, 12 courses, 22 subjects, 575 classes, 5 evaluations, 14 grades.

Test fixtures (gimsipei_test, fully owned by tests):
  3 admins, 8 teachers, 50 students, 12 courses, 27 subjects, 60
  course_subjects, 500 classes, 30 evaluations, 200 grades.
"""
import random
from datetime import UTC, datetime
from pathlib import Path

# Load test env BEFORE importing any app code, so the engine points to
# the test DB (localhost) instead of production.
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env.test", override=True)

from werkzeug.security import generate_password_hash  # noqa: E402

from src.database.database import Base, SessionLocal  # noqa: E402
from src.models.class_model import ClassModel  # noqa: E402
from src.models.course import Course  # noqa: E402
from src.models.course_student import CourseStudent  # noqa: E402
from src.models.course_subject import CourseSubject  # noqa: E402
from src.models.evaluation import Evaluation  # noqa: E402
from src.models.grade import Grade  # noqa: E402
from src.models.subject import Subject  # noqa: E402
from src.models.user import User, UserRole  # noqa: E402

PASSWORD = "Test1234!"
GRADE_LEVELS = ["1°", "2°", "3°", "4°", "5°", "6°", "7°", "8°", "9°", "10°", "11°"]
GROUPS = ["A", "B"]
YEAR = "2026"

# Deterministic seed so reruns are reproducible
random.seed(42)


def _password_hash() -> str:
    return generate_password_hash(PASSWORD)


def _seed_users(db) -> dict:
    """Create 3 admins, 8 teachers, 50 students. Return dict by role."""
    users = {"admin": [], "teacher": [], "student": []}

    # 3 admins
    for i in range(1, 4):
        u = User(
            username=f"admin_{i:02d}",
            document=f"1000000{i:02d}",
            hashed_password=_password_hash(),
            full_name=f"Admin User {i}",
            role=UserRole.ADMIN,
            is_active=1,
        )
        db.add(u)
        users["admin"].append(u)

    # 8 teachers
    for i in range(1, 9):
        u = User(
            username=f"teacher_{i:02d}",
            document=f"2000000{i:02d}",
            hashed_password=_password_hash(),
            full_name=f"Docente {i}",
            role=UserRole.TEACHER,
            is_active=1,
        )
        db.add(u)
        users["teacher"].append(u)

    # 50 students
    for i in range(1, 51):
        u = User(
            username=f"student_{i:02d}",
            document=f"300000{i:03d}",
            hashed_password=_password_hash(),
            full_name=f"Estudiante {i}",
            role=UserRole.STUDENT,
            is_active=1,
        )
        db.add(u)
        users["student"].append(u)

    db.flush()
    return users


def _seed_subjects(db) -> list[Subject]:
    """Create the 27 subjects we expect to see in the dropdown."""
    names = [
        "Matemáticas",
        "Español",
        "Ciencias Naturales",
        "Ciencias Sociales",
        "Inglés",
        "Educación Física",
        "Arte",
        "Música",
        "Religión",
        "Ética y Valores",
        "Tecnología e Informática",
        "Química",
        "Física",
        "Biología",
        "Historia",
        "Geografía",
        "Filosofía",
        "Economía",
        "Dimensión cognitiva",
        "Dimensión comunicativa",
        "Dimensión artística",
        "Dimensión corporal",
        "Dimensión socio-emocional",
        "Álgebra",
        "Aritmética",
        "Geometría",
        "Trigonometría",
    ]
    subjects = []
    for name in names:
        s = Subject(name=name)
        db.add(s)
        subjects.append(s)
    db.flush()
    return subjects


def _seed_courses(db, admin) -> list[Course]:
    """Create 12 courses."""
    courses = []
    combos = [(g, lvl) for g in GROUPS for lvl in GRADE_LEVELS[:6]]  # 12 combos
    for group, level in combos:
        c = Course(
            academic_year=YEAR,
            name=f"{level} {group}",
            created_by=admin.id,
        )
        db.add(c)
        courses.append(c)
    db.flush()
    return courses


def _seed_course_subjects(db, courses, subjects, teachers) -> list[CourseSubject]:
    """60 course_subjects — ~5 subjects per course, with rotating teachers."""
    cs_list = []
    for c in courses:
        # 5 random subjects per course
        chosen_subjects = random.sample(subjects, k=5)
        for s in chosen_subjects:
            cs = CourseSubject(
                course_id=c.id,
                subject_id=s.id,
                teacher_id=random.choice(teachers).id,
                assigned_at=datetime.now(UTC),
                is_active=True,
            )
            db.add(cs)
            cs_list.append(cs)
    db.flush()
    return cs_list


def _seed_enrollments(db, courses, students) -> list[CourseStudent]:
    """Enroll each student in 1-3 courses."""
    enrollments = []
    for stu in students:
        for c in random.sample(courses, k=random.randint(1, 3)):
            cs = CourseStudent(course_id=c.id, student_id=stu.id)
            db.add(cs)
            enrollments.append(cs)
    db.flush()
    return enrollments


def _seed_classes(db, courses, subjects, teachers) -> list[ClassModel]:
    """500 classes distributed across (course, subject) pairs."""
    classes = []
    counter = 1
    for c in courses:
        # ~8 classes per course, spread across subjects
        c_subjects = list({s.id for s in random.sample(subjects, k=8)})
        for s_id in c_subjects:
            for n in range(1, 5):  # 4 classes per subject
                if counter > 500:
                    break
                teacher = random.choice(teachers)
                cls = ClassModel(
                    course_id=c.id,
                    subject_id=s_id,
                    title=f"Clase {counter} - {c.name}",
                    description=f"Descripcion de la clase {counter}",
                    class_number=n,
                    created_by=teacher.id,
                    period=random.choice([1, 2, 3, 4]),
                )
                db.add(cls)
                classes.append(cls)
                counter += 1
        if counter > 500:
            break
    db.flush()
    return classes


def _seed_evaluations(db, courses, subjects, teachers) -> list[Evaluation]:
    """30 evaluations."""
    evals = []
    for i in range(1, 31):
        c = random.choice(courses)
        s = random.choice(subjects)
        t = random.choice(teachers)
        e = Evaluation(
            course_id=c.id,
            subject_id=s.id,
            title=f"Evaluacion {i}",
            description=f"Descripcion de la evaluacion {i}",
            period=random.choice([1, 2, 3, 4]),
            created_by=t.id,
        )
        db.add(e)
        evals.append(e)
    db.flush()
    return evals


def _seed_grades(db, enrollments, subjects) -> list[Grade]:
    """200 grades — one per (student, course, subject, period)."""
    grades = []
    for cs in random.sample(enrollments, k=min(200, len(enrollments))):
        s = random.choice(subjects)
        for period in [1, 2, 3, 4]:
            if len(grades) >= 200:
                break
            g = Grade(
                student_id=cs.student_id,
                course_id=cs.course_id,
                subject_id=s.id,
                period=period,
                tasks_grade=round(random.uniform(1.0, 5.0), 1),
                assignments_grade=round(random.uniform(1.0, 5.0), 1),
                evaluations_grade=round(random.uniform(1.0, 5.0), 1),
                final_grade=round(random.uniform(1.0, 5.0), 1),
            )
            db.add(g)
            grades.append(g)
    db.flush()
    return grades


def seed_all() -> None:
    """Seed the test database. Idempotent (truncates first)."""
    db = SessionLocal()
    try:
        # Drop and recreate everything. Idempotent and safe even on
        # a totally empty DB (TRUNCATE would fail on missing tables).
        from src.database.database import engine

        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        users = _seed_users(db)
        admin = users["admin"][0]
        teachers = users["teacher"]
        students = users["student"]
        subjects = _seed_subjects(db)
        courses = _seed_courses(db, admin)
        _seed_course_subjects(db, courses, subjects, teachers)
        enrollments = _seed_enrollments(db, courses, students)
        _seed_classes(db, courses, subjects, teachers)
        _seed_evaluations(db, courses, subjects, teachers)
        _seed_grades(db, enrollments, subjects)

        db.commit()
    finally:
        db.close()
